import logging
from pathlib import Path
from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

    def dispatch(self, request, *args, **kwargs):
        self.recipe_id = kwargs.get('recipe_id')
        self.recipe_instance = None
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
            queryset = self.recipe_instance.ingredients.all() if self.recipe_instance else RecipeIngredient.objects.none()
            kwargs.update({
                'prefix': 'recipe_ingredient',
                'queryset': queryset,
            })
            return RecipeIngredientFormSet(**kwargs)
        elif step == '2':
            queryset = self.recipe_instance.preparation_steps.all() if self.recipe_instance else RecipePreparationStep.objects.none()
            kwargs.update({
                'queryset': queryset,
                'prefix': 'recipe_preparation_step',
            })
            return RecipePreparationStepFormSet(**kwargs)
        elif step == '3':
            queryset = self.recipe_instance.images.all()
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

        # Process recipe ingredients
        ingredient_formset = self.get_form(
            step='1',
            data=self.storage.get_step_data('1')
        )

        if not ingredient_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='1', form=ingredient_formset)

        ingredients = ingredient_formset.save(commit=False)
        for ingredient in ingredients:
            ingredient.recipe = recipe
            ingredient.save()
        for obj in ingredient_formset.deleted_forms:
            obj.delete()

        print(f"{ingredients=}")

        # Process recipe preparation steps
        recipe_preparation_step_formset = self.get_form(
            step='2',
            data=self.storage.get_step_data('2')
        )

        if not recipe_preparation_step_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='2', form=recipe_preparation_step_formset)

        steps = recipe_preparation_step_formset.save(commit=False)
        for obj in recipe_preparation_step_formset.deleted_forms:
            obj.delete()
        for step in steps:
            step.recipe = recipe
            step.save()

        # Process recipe images

        print(self.storage.get_step_data('3'))
        image_formset = self.get_form(
            step='3',
            data=self.storage.get_step_data('3'),
            files=self.storage.get_step_files('3')
        )

        if not image_formset.is_valid():
            self.storage.extra_data['recipe_id'] = recipe.id
            return self.render_revalidation_failure(step='3', form=image_formset)

        # images = image_formset.save(commit=False)

        print(dir(image_formset))

        # for obj in image_formset.deleted_forms:
        #     obj.delete()

        images = image_formset.save(commit=False)
        for idx, image in enumerate(images):
            if image_formset.data.get(f"{image_formset.prefix}-{idx}-DELETE") == 'on':
                image.delete()
            else:
                image.recipe = recipe
                image.save()

        # for form in image_formset.forms:
        #     print("DELETE: ", form.data.get(f"{form.prefix}-DELETE"))
        #     if form.instance and form.data.get(f"{form.prefix}-DELETE") == 'on':
        #         form.instance.delete()
        #         image_formset.forms.remove(form)
        #     else:
        #         instance = form.save(commit=False)
        #         instance.recipe = recipe
        #         instance.save()

        return redirect(reverse('recipe-detail', kwargs={'pk': self.recipe_instance.pk}))


class RecipeDetailView(DetailView):
    model = Recipe
