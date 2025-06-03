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
            prefix = self.get_form_prefix(step)
            return RecipeIngredientFormSet(
                data=data,
                queryset=RecipeIngredient.objects.none(),
                prefix=prefix
            )
        return form

    def done(self, form_list, **kwargs):
        if form_list[0].is_valid():
            recipe = form_list[0].save(commit=False)
            recipe.created_by = self.request.user
            recipe.save()
        else:
            return self.render_revalidation_failure(step='0', form=form_list[0])

        ingredient_formset = self.get_form(step='1', data=self.storage.get_step_data('1'))

        if ingredient_formset.is_valid():
            for form in ingredient_formset:
                cleaned_data = form.cleaned_data
                if cleaned_data and not cleaned_data.get('DELETE', False):
                    ingredient = form.save(commit=False)
                    ingredient.recipe = recipe
                    ingredient.save()

                    return HttpResponse('Form successfully submitted.')
        else:
            return self.render_revalidation_failure(step='1', form=ingredient_formset)
