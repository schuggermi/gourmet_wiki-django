from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, RecipeImage


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
    empty_permitted = False

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

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        return cleaned_data


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Enter image caption (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'value': '0'
            }),
        }
