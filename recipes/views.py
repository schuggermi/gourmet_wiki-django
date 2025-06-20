import logging
from pathlib import Path
from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.forms import model_to_dict
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from formtools.wizard.views import SessionWizardView

from recipes.forms import RecipeForm, RecipeIngredientForm, RecipeImageForm, RecipePreparationStepForm
from recipes.formsets import RecipeIngredientFormSet, RecipeImageFormSet, RecipePreparationStepFormSet
from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep

User = get_user_model()


class RecipeListView(ListView):
    model = Recipe


def add_preparation_step_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipePreparationStepForm(prefix=f'recipe_preparation_step-{form_index}')

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

    print("NEW FORM: ", new_form)

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/image_form_row.html', context)
    return HttpResponse(html)


# @method_decorator(login_required, name='dispatch')
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
            self.recipe_instance = get_object_or_404(Recipe, id=self.recipe_id, created_by=request.user)
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
                queryset = self.recipe_instance.preparation_steps.all()
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
            print("Prepopulating images for recipe:", self.recipe_instance)
            for img in queryset:
                print(" -", img.pk, img.image.url)
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
            if form.data.get(f"{form.prefix}-DELETE", False):
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                instance.recipe = recipe

                exists = type(instance).objects.filter(
                    ingredient=instance.ingredient,
                    recipe=instance.recipe,
                ).exists()

                if not exists:
                    instance.save()

        # Step 2 – Preparation Steps
        step_formset = self.get_form(step='2', data=self.storage.get_step_data('2'))
        if not step_formset.is_valid():
            return self.render_revalidation_failure(step='2', form=step_formset)

        for form in step_formset:
            print("FORM DATA: ", form.data)
            print("FORM PREFIX: ", form.prefix)
            if form.data.get(f"{form.prefix}-DELETE", False):
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                instance.recipe = recipe

                exists = type(instance).objects.filter(
                    recipe=instance.recipe,
                    step_text=instance.step_text,
                ).exists()

                if not exists:
                    instance.save()

        # Step 3 – Images
        image_formset = self.get_form(
            step='3',
            data=self.storage.get_step_data('3'),
            files=self.storage.get_step_files('3')
        )
        if not image_formset.is_valid():
            return self.render_revalidation_failure(step='3', form=image_formset)

        for form in image_formset:
            if form.data.get(f"{form.prefix}-DELETE", False):
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                instance.recipe = recipe
                instance.save()

        return redirect(reverse('recipe-detail', kwargs={'pk': self.recipe_instance.pk}))


class RecipeDetailView(DetailView):
    model = Recipe
