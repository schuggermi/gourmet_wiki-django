from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory, BaseModelFormSet

from recipes.forms import RecipeIngredientForm
from recipes.models import RecipeIngredient


# class BaseRecipeIngredientFormSet(BaseModelFormSet):
#     def clean(self):
#         """
#         Checks that no duplicate ingredients exist in the formset
#         """
#         if any(self.errors):
#             return
#
#         ingredients = set()
#         for form in self.forms:
#             if form.cleaned_data and not form.cleaned_data.get('DELETE'):
#                 ingredient = form.cleaned_data.get('ingredient')
#                 if ingredient in ingredients:
#                     raise forms.ValidationError(
#                         "Each ingredient can only be used once in a recipe."
#                     )
#                 if ingredient:
#                     ingredients.add(ingredient)


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    # formset=BaseRecipeIngredientFormSet,
    extra=1,
    can_delete=False,
    validate_min=True,
)
