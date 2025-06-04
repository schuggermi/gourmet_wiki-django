from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'thumbnail_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Enter recipe name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 4
            }),
            'thumbnail_image': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'
            }),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={
                'class': 'select',
                'placeholder': 'Enter recipe name'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'input',
            }),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data.get('ingredient'):
    #         return cleaned_data
    #
    #     # if not cleaned_data.get('quantity'):
    #     #     self.add_error('quantity', 'Quantity is required for this ingredient.')
    #
    #     # # Individual form validation for existing ingredients
    #     # # The formset will handle duplicate ingredients within the current form submission
    #     # recipe = getattr(self.instance, 'recipe', None)
    #     # if recipe and not self.instance.pk:  # Only check for new ingredients
    #     #     existing = RecipeIngredient.objects.filter(
    #     #         recipe=recipe,
    #     #         ingredient=cleaned_data['ingredient']
    #     #     ).exists()
    #     #     if existing:
    #     #         raise ValidationError({
    #     #             'ingredient': 'This ingredient has already been added to the recipe.'
    #     #         })
    #     return cleaned_data
