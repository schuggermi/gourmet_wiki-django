from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.template.loader import render_to_string
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
    new_form = RecipeIngredientForm(prefix=f'form-{form_index}')

    print(f"{form_index=}")

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/ingredient_form_row.html', context)
    return HttpResponse(html)


@method_decorator(login_required, name='dispatch')
class CreateRecipeWizardView(SessionWizardView):
    form_list = [RecipeForm, RecipeIngredientForm]
    template_name = 'recipes/create_recipe_wizard.html'

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step == '1':
            print(f"{data=}")
            return RecipeIngredientFormSet(
                data=data,
                queryset=RecipeIngredient.objects.none(),
                prefix=f'recipe_ingredient'
            )
        return form
    
    def done(self, form_list, **kwargs):
        recipe_form = form_list[0]

        # if not recipe_form.is_valid():
        #     return self.render_revalidation_failure(step='0', form=recipe_form)

        recipe = recipe_form.save(commit=False)
        recipe.created_by = self.request.user
        recipe.save()

        ingredient_formset = self.get_form(
            step='1',
            data=self.storage.get_step_data('1')
        )

        # ingredients_used = set()
        # has_duplicates = False
        #
        # for form in ingredient_formset:
        #     if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
        #         continue
        #
        #     ingredient = form.cleaned_data.get('ingredient')
        #     if ingredient in ingredients_used:
        #         form.add_error('ingredient', 'This ingredient has already been added to this recipe.')
        #         has_duplicates = True
        #     ingredients_used.add(ingredient)
        #
        # if has_duplicates:
        #     self.storage.extra_data['recipe_id'] = recipe.id
        #     return self.render_revalidation_failure(step='1', form=ingredient_formset)

        # If we get here, no duplicates were found, save all ingredients
        for form in ingredient_formset:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                recipe_ingredient = form.save(commit=False)
                recipe_ingredient.recipe = recipe
                recipe_ingredient.save()

        return HttpResponse('Form successfully submitted.')
