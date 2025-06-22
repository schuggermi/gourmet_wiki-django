from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep

INPUT_CLASSES = ''
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
                'placeholder': 'Name your creation (e.g. Spicy Thai Basil Chicken)',
                'maxlength': Recipe._meta.get_field('name').max_length,
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20,
                'wrap': 'soft',
                'resize': False,
                'placeholder': 'e.g. A spicy Thai stir-fry with chicken, basil, and fresh chili.',
                'maxlength': Recipe._meta.get_field('description').max_length,
            }),
            # 'thumbnail_image': forms.FileInput(attrs={
            #     'class': FILE_INPUT_CLASSES,
            #     'accept': 'image/*'
            # }),
            'skill_level': forms.Select(attrs={
                'placeholder': 'Choose a Skill Level'
            }),
            'portions': forms.NumberInput(attrs={
                'min': 1,
                'max': 500,
            }),
            'working_time_hours': forms.NumberInput(attrs={
                'min': 0,
                'max': 24,
            }),
            'working_time_minutes': forms.NumberInput(attrs={
                'min': 0,
                'max': 60,
            }),
            'cooking_time_hours': forms.NumberInput(attrs={
                'min': 0,
                'max': 24,
            }),
            'cooking_time_minutes': forms.NumberInput(attrs={
                'min': 0,
                'max': 60,
            }),
            'rest_time_hours': forms.NumberInput(attrs={
                'min': 0,
                'max': 24,
            }),
            'rest_time_minutes': forms.NumberInput(attrs={
                'min': 0,
                'max': 60,
            }),
        }


class RecipePreparationStepForm(forms.ModelForm):
    class Meta:
        model = RecipePreparationStep
        fields = ['step_text', 'order']
        widgets = {
            'step_text': forms.TextInput(attrs={
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
            'ingredient': forms.TextInput(attrs={
                'placeholder': 'Butter'
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity'
            }),
            'unit': forms.Select(attrs={
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
        fields = ['image', 'caption', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
            }),
            'caption': forms.TextInput(attrs={
                'placeholder': 'Image caption (optional)'
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

    def clean_image(self):
        image = self.cleaned_data.get('image')

        if not image and self.instance and self.instance.pk:
            return self.instance.image
        return image

    # def clean(self):
    #     cleaned_data = super().clean()
    #     image = cleaned_data.get('image')
    #
    #     # If no new image is uploaded, but the instance has one, reuse it
    #     if not image and self.instance and self.instance.pk and self.instance.image:
    #         cleaned_data['image'] = self.instance.image
    #
    #     # If still no image, raise error
    #     if not image:
    #         self.add_error('image', "This field is requiredd.")
    #
    #     return cleaned_data
