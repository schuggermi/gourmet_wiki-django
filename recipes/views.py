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

from recipes.forms import RecipeForm, RecipeIngredientForm
from recipes.formsets import RecipeIngredientFormSet
from recipes.models import Recipe, RecipeIngredient

User = get_user_model()


class RecipeListView(ListView):
    model = Recipe


def add_ingredient_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipeIngredientForm(prefix=f'recipe_ingredient-{form_index}')

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/ingredient_form_row.html', context)
    return HttpResponse(html)


@method_decorator(login_required, name='dispatch')
class CreateRecipeWizardView(SessionWizardView):
    form_list = [
        ('0', RecipeForm),
        ('1', RecipeIngredientFormSet),
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
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        recipe_form = self.get_form(step='0', data=self.storage.get_step_data('0'), files=self.storage.get_step_files('0'))

        if not recipe_form.is_valid():
            return self.render_revalidation_failure(step='0', form=recipe_form)

        recipe = recipe_form.save(commit=False)
        recipe.created_by = self.request.user
        recipe.save()

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

        messages.success(
            self.request, 
            f'Recipe "{recipe.name}" successfully created with {ingredients_count} ingredients!'
        )
        return redirect(reverse('recipe-list'))
