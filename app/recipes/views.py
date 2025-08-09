from pathlib import Path
from pprint import pprint

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, DetailView
from formtools.wizard.views import SessionWizardView

from menus.models import Menu
from recipes.forms import RecipeForm, RecipeIngredientForm, RecipeImageForm, RecipePreparationStepForm
from recipes.formsets import RecipeIngredientFormSet, RecipeImageFormSet, RecipePreparationStepFormSet
from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep, RecipeRating
from recipes.utils import calculate_scaled_ingredients_menu

User = get_user_model()


class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.filter(is_published=True)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


def recipe_list_partial(request):
    """
    View to render the recipe list partial for htmx requests
    """
    queryset = Recipe.objects.all()

    queryset = queryset.filter(is_published=True)

    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    context = {
        'object_list': queryset,
        'search_query': search_query,
    }

    return render(request, 'recipes/partials/recipe_list.html', context)


def add_preparation_step_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipePreparationStepForm(prefix=f'recipe_preparation_step-{form_index}')

    new_form.fields['DELETE'] = forms.BooleanField(required=False)
    new_form.fields['ORDER'] = forms.IntegerField(required=True)

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/preparation_step_form_row.html', context)
    return HttpResponse(html)


def add_ingredient_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipeIngredientForm(prefix=f'recipe_ingredient-{form_index}')

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/ingredient_form_row.html', context)
    return HttpResponse(html)


def add_image_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipeImageForm(prefix=f'recipe_image-{form_index}')

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/image_form_row.html', context)
    return HttpResponse(html)


class CreateRecipeWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ('0', RecipeForm),
        ('1', RecipeIngredientFormSet),
        ('2', RecipePreparationStepFormSet),
        ('3', RecipeImageFormSet),
    ]
    template_name = 'recipes/create_recipe_wizard.html'
    file_storage = FileSystemStorage(location=Path(settings.MEDIA_ROOT).joinpath('recipes/images/temp'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipe_id = None
        self.recipe_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.recipe_id = kwargs.get('recipe_id')
        if self.recipe_id:
            self.recipe_instance = get_object_or_404(Recipe, id=self.recipe_id, created_by=request.user.pk)
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
            if self.recipe_instance:
                kwargs['instance'] = self.recipe_instance
            return RecipeForm(**kwargs)
        elif step == '1':
            if self.recipe_instance:
                queryset = self.recipe_instance.ingredients.all()
            else:
                queryset = RecipeIngredient.objects.none()
            kwargs.update({
                'prefix': 'recipe_ingredient',
                'queryset': queryset,
            })
            return RecipeIngredientFormSet(**kwargs)
        elif step == '2':
            if self.recipe_instance:
                queryset = self.recipe_instance.preparation_steps.all().order_by('order')
            else:
                queryset = RecipePreparationStep.objects.none()
            kwargs.update({
                'queryset': queryset,
                'prefix': 'recipe_preparation_step',
            })
            return RecipePreparationStepFormSet(**kwargs)
        elif step == '3':
            if self.recipe_instance:
                queryset = self.recipe_instance.images.all()
            else:
                queryset = RecipeImage.objects.none()
            kwargs.update({
                'queryset': queryset,
                'prefix': 'recipe_image',
            })
            return RecipeImageFormSet(**kwargs)
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        recipe_form = self.get_form(
            step='0',
            data=self.storage.get_step_data('0'),
            files=self.storage.get_step_files('0')
        )

        if not recipe_form.is_valid():
            return self.render_revalidation_failure(step='0', form=recipe_form)

        if self.recipe_instance:
            recipe = recipe_form.save()
        else:
            recipe = recipe_form.save(commit=False)
            recipe.created_by = self.request.user
            recipe.save()

        # Step 1 – Ingredients
        ingredient_formset = self.get_form(step='1', data=self.storage.get_step_data('1'))
        if not ingredient_formset.is_valid():
            return self.render_revalidation_failure(step='1', form=ingredient_formset)

        for form in ingredient_formset:
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                instance.recipe = recipe
                print("CLEANED INGREDIENT: ", form.cleaned_data['ingredient'])
                instance.ingredient = form.cleaned_data['ingredient']

                pprint(instance, indent=4)

                instance.save()

        # Step 2 – Preparation Steps
        step_formset = self.get_form(step='2', data=self.storage.get_step_data('2'))
        if not step_formset.is_valid():
            return self.render_revalidation_failure(step='2', form=step_formset)

        for index, form in enumerate(step_formset):
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)

                if not instance.pk:
                    instance.recipe = recipe
                instance.order = form.cleaned_data.get('order', index)
                instance.save()

        # Step 3 – Images
        image_formset = self.get_form(
            step='3',
            data=self.storage.get_step_data('3'),
            files=self.storage.get_step_files('3')
        )
        if not image_formset.is_valid():
            return self.render_revalidation_failure(step='3', form=image_formset)

        for index, form in enumerate(image_formset):
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                if not instance.pk:
                    instance.recipe = recipe
                instance.order = form.cleaned_data.get('order', index)
                instance.save()

        return redirect(reverse('recipe-detail', kwargs={'pk': recipe.pk}))


class RecipeDetailView(DetailView):
    model = Recipe


def get_calculate_scaled_ingredients(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'ingredients': recipe.calculate_scaled_ingredients(int(request.GET.get('portions', recipe.portions)))
    }

    html = render_to_string('recipes/partials/recipe_ingredients_list.html', context)
    return HttpResponse(html)


def get_calculate_scaled_ingredients_menu(request, menu_id):
    context = calculate_scaled_ingredients_menu(menu_id, int(request.GET.get('portions')))
    context['current_recipe_slide'] = request.GET.get('current_recipe_slide', 0)

    html = render_to_string('menus/partials/recipe_carousel.html', context)
    return HttpResponse(html)


@login_required
def toggle_favorite(request, recipe_id):
    if request.method != "POST":
        return HttpResponseForbidden()

    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user

    if user in recipe.favorite_by.all():
        recipe.favorite_by.remove(user)
    else:
        recipe.favorite_by.add(user)
    html = render_to_string(
        "recipes/partials/favorite_button.html",
        {"recipe": recipe, "user": user},
        request=request
    )
    return HttpResponse(html)


@login_required
def rate_recipe(request, recipe_id, score):
    if request.method != "POST":
        return HttpResponseForbidden()

    recipe = get_object_or_404(Recipe, id=recipe_id)

    rating, created = RecipeRating.objects.update_or_create(
        recipe=recipe,
        user=request.user,
        defaults={'score': score}
    )

    average_rating = recipe.average_rating

    return render(request, "cotton/rating_action.html", {
        "recipe": recipe,
        "average_rating": average_rating,
        "score": score,
    })
