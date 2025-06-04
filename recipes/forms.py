from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description']


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity']

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data.get('ingredient'):
    #         return cleaned_data
    #
    #     recipe = getattr(self.instance, 'recipe', None)
    #     if recipe:
    #         existing = RecipeIngredient.objects.filter(
    #             recipe=recipe,
    #             ingredient=cleaned_data['ingredient']
    #         ).exists()
    #         if existing:
    #             raise ValidationError({
    #                 'ingredient': 'This ingredient has already been added to the recipe.'
    #             })
    #     return cleaned_data
