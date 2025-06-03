from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory, BaseModelFormSet

from recipes.forms import RecipeIngredientForm
from recipes.models import RecipeIngredient


# class BaseRecipeIngredientFormSet(BaseModelFormSet):
#     def clean(self):
#         super().clean()
#         if any(self.errors):
#             return  # Skip if individual forms have errors already
#
#         seen = set()
#         for form in self.forms:
#             if form.cleaned_data.get('DELETE', False):
#                 continue
#
#             recipe = form.cleaned_data.get('recipe')  # might be None at creation time
#             ingredient = form.cleaned_data.get('ingredient')
#
#             # We'll use (ingredient) only here because recipe is not assigned yet
#             # Handle it later in the wizard `done()`
#             key = ingredient.id if ingredient else None
#             if key in seen:
#                 raise ValidationError("Each ingredient must be unique.")
#             seen.add(key)


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    # formset=BaseRecipeIngredientFormSet,
    extra=1,
    can_delete=False,
)
