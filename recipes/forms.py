from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep

INPUT_CLASSES = 'input bg-base-content rounded-sm w-full'
NUMBER_INPUT_CLASSES = 'input bg-base-content rounded-sm w-full'
SELECT_CLASSES = 'select bg-base-content rounded-sm w-full'
TEXTAREA_CLASSES = 'textarea bg-base-content rounded-sm w-full border-box focus:outline-none focus:border-none'
FILE_INPUT_CLASSES = 'file-input bg-base-content rounded-sm w-full'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name', 'description', 'skill_level', 'portions', 'working_time_hours', 'working_time_minutes',
            'cooking_time_hours', 'cooking_time_minutes', 'rest_time_hours', 'rest_time_minutes',
        ]  # thumbnail_image
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Name your creation (e.g. Spicy Thai Basil Chicken)'
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASSES + ' resize-none',
                'rows': 3,
                'cols': 20,
                'wrap': 'soft',
                'style': 'white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;',
                'placeholder': 'e.g. A spicy Thai stir-fry with chicken, basil, and fresh chili.'
            }),
            # 'thumbnail_image': forms.FileInput(attrs={
            #     'class': FILE_INPUT_CLASSES,
            #     'accept': 'image/*'
            # }),
            'skill_level': forms.Select(attrs={
                'class': SELECT_CLASSES,
                'placeholder': 'Choose a Skill Level'
            }),
            'portions': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 1,
                'max': 500,
            }),
            'working_time_hours': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 24,
            }),
            'working_time_minutes': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 60,
            }),
            'cooking_time_hours': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 24,
            }),
            'cooking_time_minutes': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 60,
            }),
            'rest_time_hours': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 24,
            }),
            'rest_time_minutes': forms.NumberInput(attrs={
                'class': NUMBER_INPUT_CLASSES,
                'min': 0,
                'max': 60,
            }),
        }


class RecipePreparationStepForm(forms.ModelForm):
    class Meta:
        model = RecipePreparationStep
        fields = ['step_text']
        widgets = {
            'step_text': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g. Heat 2 tbsp of oil in a wok over medium-high heat.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if self.errors.get(field_name):
                old_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = (
                        old_class + ' border-3 border-red-400'
                )

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        step_text = cleaned_data.get('step_text')

        if not step_text:
            self.add_error('step_text', 'This field is required.')

        return cleaned_data


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if self.errors.get(field_name):
                old_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = (
                        old_class + ' border-3 border-red-400'
                )

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
