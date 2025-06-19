from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
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

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/image_form_row.html', context)
    return HttpResponse(html)


@method_decorator(login_required, name='dispatch')
class CreateRecipeWizardView(SessionWizardView):
    form_list = [
        ('0', RecipeForm),
        ('1', RecipeIngredientFormSet),
        ('2', RecipePreparationStepFormSet),
        ('3', RecipeImageFormSet),
    ]
    template_name = 'recipes/create_recipe_wizard.html'
    file_storage = FileSystemStorage(location=Path(settings.MEDIA_ROOT).joinpath('recipes/images/temp'))

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        if step == '1':
            return RecipeIngredientFormSet(
                data=data,
                queryset=RecipeIngredient.objects.none(),
                prefix='recipe_ingredient'
            )
        elif step == '2':
            return RecipePreparationStepFormSet(
                data=data,
                files=files,
                queryset=RecipePreparationStep.objects.none(),
                prefix='recipe_preparation_step'
            )
        elif step == '3':
            return RecipeImageFormSet(
                data=data,
                files=files,
                queryset=RecipeImage.objects.none(),
                prefix='recipe_image'
            )
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        recipe_form = self.get_form(step='0', data=self.storage.get_step_data('0'),
                                    files=self.storage.get_step_files('0'))

        if not recipe_form.is_valid():
            return self.render_revalidation_failure(step='0', form=recipe_form)

        recipe = recipe_form.save(commit=False)
        recipe.created_by = self.request.user
        recipe.save()

        # Process recipe ingredients
        ingredient_formset = self.get_form(
            step='1',
            data=self.storage.get_step_data('1')
        )

        if not ingredient_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='1', form=ingredient_formset)

        ingredients_count = 0
        for form in ingredient_formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                recipe_ingredient = form.save(commit=False)
                recipe_ingredient.recipe = recipe
                recipe_ingredient.save()
                ingredients_count += 1

        # Process recipe preparation steps
        recipe_preparation_step_formset = self.get_form(
            step='2',
            data=self.storage.get_step_data('2')
        )

        if not recipe_preparation_step_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='2', form=recipe_preparation_step_formset)

        prep_steps_count = 0
        for form in recipe_preparation_step_formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                recipe_prep_step = form.save(commit=False)
                recipe_prep_step.recipe = recipe
                recipe_prep_step.save()
                prep_steps_count += 1

        # Process recipe images
        image_formset = self.get_form(
            step='3',
            data=self.storage.get_step_data('3'),
            files=self.storage.get_step_files('3')
        )

        if not image_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='3', form=image_formset)

        images_count = 0
        for form in image_formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False) and form.cleaned_data.get('image'):
                recipe_image = form.save(commit=False)
                recipe_image.recipe = recipe
                recipe_image.save()
                images_count += 1

        return redirect(reverse('users-profile-recipes'))
