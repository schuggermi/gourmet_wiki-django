from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView
from formtools.wizard.views import SessionWizardView

from menus.forms import MenuForm, MenuCourseForm
from menus.formsets import MenuCourseFormSet
from menus.models import Menu, MenuCourse
from recipes.utils import calculate_scaled_ingredients_menu


def add_menu_course_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = MenuCourseForm(prefix=f'menu_course-{form_index}')

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('menus/partials/menu_course_form_row.html', context)
    return HttpResponse(html)


class MenuListView(ListView):
    model = Menu


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
                queryset = self.menu_instance.get_course_types
            else:
                queryset = MenuCourse.objects.none()
            kwargs.update({
                'prefix': 'menu_course',
                'queryset': queryset,
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
            print("Menu form validation failed")
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
            print("Courses formset validation failed")
            return self.render_revalidation_failure(step='1', form=courses_formset)

        for index, form in enumerate(courses_formset):
            if form.data.get(f"{form.prefix}-DELETE", False):
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                if not instance.pk:
                    instance.menu = menu
                instance.order = form.cleaned_data.get('order', index)
                instance.course_type = form.cleaned_data['course_type']
                instance.save()

        return redirect(reverse('menu_detail', kwargs={'pk': menu.id}))
