from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep, RecipeRating

from ingredients.models import Ingredient

INPUT_CLASSES = ''
NUMBER_INPUT_CLASSES = 'input bg-base-content rounded-sm w-full'
SELECT_CLASSES = 'select bg-base-content rounded-sm w-full'
TEXTAREA_CLASSES = 'textarea bg-base-content rounded-sm w-full border-box focus:outline-none focus:border-none'
FILE_INPUT_CLASSES = 'file-input bg-base-content rounded-sm w-full'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'name', 'is_published', 'description', 'skill_level', 'portions', 'cooking_time_hours',
            'cooking_time_minutes',
        ]  # 'thumbnail_image', 'rest_time_hours', 'rest_time_minutes', 'working_time_hours', 'working_time_minutes'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': _("Name your creation (e.g. Spicy Thai Basil Chicken)"),
                'maxlength': Recipe._meta.get_field('name').max_length,
            }),
            'is_published': forms.CheckboxInput(attrs={}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20,
                'wrap': 'soft',
                'resize': False,
                'placeholder': _("e.g. A spicy Thai stir-fry with chicken, basil, and fresh chili."),
                'maxlength': Recipe._meta.get_field('description').max_length,
            }),
            # 'thumbnail_image': forms.FileInput(attrs={
            #     'class': FILE_INPUT_CLASSES,
            #     'accept': 'image/*'
            # }),
            'skill_level': forms.Select(),
            'portions': forms.NumberInput(attrs={
                'min': 1,
                'max': 500,
            }),
            # 'working_time_hours': forms.NumberInput(attrs={
            #     'min': 0,
            #     'max': 24,
            # }),
            # 'working_time_minutes': forms.NumberInput(attrs={
            #     'min': 0,
            #     'max': 60,
            # }),
            'cooking_time_hours': forms.NumberInput(attrs={
                'min': 0,
                'max': 24,
            }),
            'cooking_time_minutes': forms.NumberInput(attrs={
                'min': 0,
                'max': 60,
            }),
            # 'rest_time_hours': forms.NumberInput(attrs={
            #     'min': 0,
            #     'max': 24,
            # }),
            # 'rest_time_minutes': forms.NumberInput(attrs={
            #     'min': 0,
            #     'max': 60,
            # }),
        }


class RecipePreparationStepForm(forms.ModelForm):
    class Meta:
        model = RecipePreparationStep
        fields = ['step_text']
        widgets = {
            'step_text': forms.TextInput(attrs={
                'placeholder': _("e.g. Heat 2 tbsp of oil in a wok over medium-high heat.")
            }),
        }

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
            'ingredient': forms.HiddenInput(),  # hide actual ingredient field
            'quantity': forms.NumberInput(attrs={'placeholder': '0'}),
            'unit': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ingredient is no longer required from the HTML form
        self.fields['ingredient'].required = False

    # def clean(self):
    #     cleaned_data = super().clean()
    #
    #     # If ingredient is missing but q is present in POST data
    #     if not cleaned_data.get('ingredient'):
    #         q_val = self.data.get(f"{self.prefix}-q") or self.data.get('q')
    #         if q_val:
    #             # Get the current language
    #             current_lang = translation.get_language()
    #
    #             # Try to find the ingredient by name or translation
    #             ingredient_obj = Ingredient.objects.filter(
    #                 Q(name=q_val) |
    #                 Q(translations__name=q_val, translations__language_code=current_lang)
    #             ).first()
    #
    #             if ingredient_obj:
    #                 cleaned_data['ingredient'] = ingredient_obj
    #             else:
    #                 self.add_error('ingredient', f"No ingredient found for '{q_val}'")
    #
    #     return cleaned_data


class RatingForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = ['score']


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = RecipeImage
        fields = ['image', 'caption']
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
        if not image and not self.instance.image:
            raise forms.ValidationError(_("This field is required."))
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
