from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, DetailView
from formtools.wizard.views import SessionWizardView

from menus.forms import MenuForm, MenuCourseForm, MenuItemForm
from menus.formsets import MenuCourseFormSet, MenuItemFormSet
from menus.models import Menu, MenuCourse, MenuItem
from recipes.models import Recipe
from recipes.utils import calculate_scaled_ingredients_menu


def add_menu_course_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = MenuCourseForm(prefix=f'menu_course-{form_index}', user=request.user)

    new_form.fields['DELETE'] = forms.BooleanField(required=False)
    new_form.fields['ORDER'] = forms.IntegerField(required=True)

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('menus/partials/menu_course_form_row.html', context)
    return HttpResponse(html)


def add_menu_item_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = MenuItemForm(prefix=f'menu_item-{form_index}', user=request.user)

    new_form.fields['DELETE'] = forms.BooleanField(required=False)

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('menus/partials/menu_item_form_row.html', context)
    return HttpResponse(html)


def get_recipes_by_course_type(request):
    """
    AJAX view to get recipes filtered by course_type
    """
    course_type = request.GET.get('course_type')
    form_prefix = request.GET.get('form_prefix')

    if not course_type:
        return JsonResponse({'error': 'Course type is required'}, status=400)

    # Get recipes filtered by course_type and user (created or favorited)
    recipes = Recipe.objects.filter(
        course_type=course_type
    ).filter(
        Q(created_by=request.user) | Q(favorite_by=request.user)
    ).distinct()

    # Format recipes as options for select field
    recipe_options = [{'value': recipe.id, 'text': recipe.name} for recipe in recipes]

    return JsonResponse({
        'recipes': recipe_options,
        'form_prefix': form_prefix
    })


def menu_list_partial(request):
    """
    View to render the menu list partial for htmx requests
    """
    queryset = Menu.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    context = {
        'object_list': queryset,
        'search_query': search_query,
    }

    return render(request, 'menus/partials/menu_list.html', context)


class MenuListView(ListView):
    model = Menu

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class MenuDetailView(DetailView):
    model = Menu

    def get_context_data(self, **kwargs):
        context = super(MenuDetailView, self).get_context_data(**kwargs)
        context.update(calculate_scaled_ingredients_menu(self.object.pk, self.object.portions))
        return context


# class MenuCreateView(LoginRequiredMixin, CreateView):
#     model = Menu
#     fields = ['name', 'menu_type', 'portions']
#     template_name = 'menus/menu_form.html'


class CreateMenuWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ('0', MenuForm),
        ('1', MenuCourseFormSet),
    ]
    template_name = 'menus/create_menu_wizard.html'
    file_storage = FileSystemStorage(location=Path(settings.MEDIA_ROOT).joinpath('menus/images/temp'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_id = None
        self.menu_instance = None
        self.menu_course_instances = {}
        self.menu_courses = {}

    def dispatch(self, request, *args, **kwargs):
        self.menu_id = kwargs.get('menu_id')
        if self.menu_id:
            self.menu_instance = get_object_or_404(Menu, id=self.menu_id, created_by=request.user.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        kwargs = {}

        if data is not None:
            kwargs['data'] = data
        if files is not None:
            kwargs['files'] = files

        if step == '0':
            if self.menu_instance:
                kwargs['instance'] = self.menu_instance
            return MenuForm(**kwargs)
        elif step == '1':
            if self.menu_instance:
                queryset = self.menu_instance.courses.all()
            else:
                queryset = MenuCourse.objects.none()

            # Get the form kwargs for each form in the formset
            form_kwargs = {'user': self.request.user}

            kwargs.update({
                'prefix': 'menu_course',
                'queryset': queryset,
                'form_kwargs': form_kwargs,
            })
            return MenuCourseFormSet(**kwargs)
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        menu_form = self.get_form(
            step='0',
            data=self.storage.get_step_data('0'),
            files=self.storage.get_step_files('0')
        )

        if not menu_form.is_valid():
            return self.render_revalidation_failure(step='0', form=menu_form)

        if self.menu_instance:
            menu = menu_form.save()
        else:
            menu = menu_form.save(commit=False)
            menu.created_by = self.request.user
            menu.save()

        # Step 1 – Menu Courses
        courses_formset = self.get_form(step='1', data=self.storage.get_step_data('1'))
        if not courses_formset.is_valid():
            return self.render_revalidation_failure(step='1', form=courses_formset)

        # Process all forms in the formset
        for index, form in enumerate(courses_formset):
            # Handle deleted forms
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    # If we're deleting a menu course, also delete any associated menu items
                    MenuItem.objects.filter(menu_course=form.instance).delete()
                    form.instance.delete()
                continue

            # Get the recipe from the form
            recipe = form.cleaned_data.get('recipe')
            if not recipe:
                continue

            # Save the MenuCourse instance
            menu_course = form.save(commit=False)
            menu_course.menu_id = menu.id
            menu_course.order = form.cleaned_data.get('ORDER', index)
            menu_course.save()

            # Check if a MenuItem already exists for this menu course
            menu_item, created = MenuItem.objects.get_or_create(
                menu_id=menu.id,
                menu_course=menu_course,
                defaults={'recipe': recipe}
            )

            # If the MenuItem exists but the recipe has changed, update it
            if not created and menu_item.recipe != recipe:
                menu_item.recipe = recipe
                menu_item.save()

        return redirect(reverse('menu_detail', kwargs={'pk': menu.id}))
