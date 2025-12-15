from django import forms
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
            'name', 'is_published', 'description', 'skill_level', 'portions', 'cooking_time_minutes', 'course_type'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': _("Spicy Thai Basil Chicken"),
                    'maxlength': Recipe._meta.get_field('name').max_length,
                }
            ),
            'is_published': forms.CheckboxInput(attrs={}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20,
                'wrap': 'soft',
                'resize': False,
                'placeholder': _("A spicy Thai stir-fry with chicken, basil, and fresh chili."),
                'maxlength': Recipe._meta.get_field('description').max_length,
            }),
            'skill_level': forms.Select(),
            'portions': forms.NumberInput(attrs={
                'min': 1,
                'max': 500,
            }),
            'cooking_time_minutes': forms.NumberInput(attrs={
                'min': 0,
                'max': 60,
            }),
            'course_type': forms.Select(),
        }


class RecipePreparationStepForm(forms.ModelForm):
    class Meta:
        model = RecipePreparationStep
        fields = ['is_section', 'section_title', 'step_text']
        widgets = {
            'step_text': forms.TextInput(attrs={
                'placeholder': _("e.g. Heat 2 tbsp of oil in a wok over medium-high heat.")
            }),
            'section_title': forms.TextInput(attrs={
                'placeholder': _("e.g. Sauce, Meat, Salad"),
            }),
            'is_section': forms.CheckboxInput(attrs={
                'class': 'checkbox'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        is_section = cleaned_data.get('is_section')
        section_title = cleaned_data.get('section_title')
        step_text = cleaned_data.get('step_text')

        if is_section:
            # Section headers must have a title; step_text is optional/ignored
            if not section_title or not section_title.strip():
                self.add_error('section_title', _('Please provide a section title.'))
            # Normalize: no step text for section rows
            cleaned_data['step_text'] = ''
        else:
            # Regular steps must have step text; section title is optional and cleared
            if not step_text or not step_text.strip():
                self.add_error('step_text', _('This field is required.'))
            cleaned_data['section_title'] = cleaned_data.get('section_title', '').strip()

        return cleaned_data


class RecipeIngredientForm(forms.ModelForm):
    ingredient_name = forms.CharField(required=True, max_length=255)

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {
            'ingredient': forms.HiddenInput(),  # hide actual ingredient field
            'quantity': forms.NumberInput(attrs={
                'placeholder': '0',
                'min': '0.1',  # Add min attribute to match model validator
                'step': '0.1',  # Allow decimal values
            }),
            'unit': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ingredient is no longer required from the HTML form
        self.fields['ingredient'].required = False

        # Set a default value for quantity to ensure it's always valid
        if not self.initial.get('quantity'):
            self.initial['quantity'] = 1.0

        # If we have an instance with an ingredient, populate the ingredient_name field
        if self.instance and self.instance.pk and self.instance.ingredient:
            self.fields['ingredient_name'].initial = self.instance.ingredient.name

    def clean(self):
        cleaned_data = super().clean()

        # We're using ingredient_name now, so we don't need to validate ingredient
        # This prevents the "Please make a valid selection" error
        if 'ingredient' in cleaned_data:
            del cleaned_data['ingredient']

        return cleaned_data


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
