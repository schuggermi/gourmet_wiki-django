from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, RecipeImage


INPUT_CLASSES = 'input input-accent bg-base-content text-base-primary w-full'
SELECT_CLASSES = 'select select-accent bg-base-content text-base-primary w-full'
TEXTAREA_CLASSES = 'textarea textarea-accent bg-base-content text-base-primary w-full resize-none'
FILE_INPUT_CLASSES = 'file-input file-input-ghost text-base-primary w-full'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description'] #thumbnail_image
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Recipe Name'
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES,
                'rows': 2,
                'placeholder': 'Recipe Description'
            }),
            # 'thumbnail_image': forms.FileInput(attrs={
            #     'class': FILE_INPUT_CLASSES,
            #     'accept': 'image/*'
            # }),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {
            'ingredient': forms.Select(attrs={
                'class': SELECT_CLASSES,
                'placeholder': 'New Ingredient'
            }),
            'quantity': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Quantity'
            }),
            'unit': forms.Select(attrs={
                'class': SELECT_CLASSES,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        # Check if both ingredient and quantity are provided
        ingredient = cleaned_data.get('ingredient')
        quantity = cleaned_data.get('quantity')

        if not ingredient:
            self.add_error('ingredient', 'This field is required.')

        if not quantity:
            self.add_error('quantity', 'This field is required.')

        return cleaned_data


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASSES,
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Image caption (optional)'
            }),
        }
