from django.forms.models import modelformset_factory, BaseModelFormSet

from recipes.forms import RecipeIngredientForm, RecipeImageForm
from recipes.models import RecipeIngredient, RecipeImage


class BaseRecipeIngredientFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        if not self.forms:
            self.non_form_errors().append("At least one ingredient is required.")

        ingredients = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                ingredient = form.cleaned_data.get('ingredient')
                if ingredient in ingredients:
                    form.add_error('ingredient', 'This ingredient has already been added to this recipe.')
                if ingredient:
                    ingredients.add(ingredient)


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
    extra=1,
    can_delete=False,
    validate_min=True,
)


class BaseRecipeImageFormSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        # No need to check for duplicates as we want to allow multiple images


RecipeImageFormSet = modelformset_factory(
    RecipeImage,
    form=RecipeImageForm,
    formset=BaseRecipeImageFormSet,
    extra=1,
    can_delete=False,
)
