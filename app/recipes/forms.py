from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.forms import fields
from django.utils.translation import gettext_lazy as _
from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep, RecipeRating
from ingredients.models import Ingredient

from core.models import SkillLevelChoice

INPUT_CLASSES = ''
NUMBER_INPUT_CLASSES = 'input bg-base-content rounded-sm w-full'
SELECT_CLASSES = 'select bg-base-content rounded-sm w-full'
TEXTAREA_CLASSES = 'textarea bg-base-content rounded-sm w-full border-box focus:outline-none focus:border-none'
FILE_INPUT_CLASSES = 'file-input bg-base-content rounded-sm w-full'


""" NEW """

class RecipeCreateForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name"]
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': _("Spicy Thai Basil Chicken"),}
            )
        }


class RecipeNameForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name"]
        widgets = {
            'name': forms.TextInput(
                attrs={'placeholder': _("Spicy Thai Basil Chicken"), }
            )
        }


class RecipePublishForm(forms.ModelForm):
    is_published = forms.BooleanField(
        label=_("Published"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput()
    )
    class Meta:
        model = Recipe
        fields = ["is_published"]


class RecipeDetailsForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["description", "course_type", "portions", "cooking_time_minutes", "skill_level"]
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'placeholder': _("A spicy Thai stir-fry with chicken, basil, and fresh chili."),
                    'rows': 3,
                    'wrap': 'soft',
                }
            ),
            'course_type': forms.Select(),
            'portions': forms.NumberInput(),
            'cooking_time_minutes': forms.NumberInput(),
            'skill_level': forms.Select(),
        }


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     # Get the model field
    #     model_field = self._meta.model._meta.get_field("name")
    #     form_field = self.fields["name"]
    #     attrs = form_field.widget.attrs
    #
    #     # # Check for MinLengthValidator in existing validators
    #     # min_length = getattr(model_field, 'min_length', None)
    #     # if not min_length:
    #     #     # Check if it's in validators
    #     #     min_length = next(
    #     #         (v.limit_value for v in model_field.validators if isinstance(v, MinLengthValidator)),
    #     #         None,
    #     #     )
    #     #
    #     # if min_length:
    #     #     attrs["minlength"] = min_length
    #     #     # Ensure the form field also validates this
    #     #     if not any(isinstance(v, MinLengthValidator) for v in form_field.validators):
    #     #         form_field.validators.append(MinLengthValidator(min_length))
    #
    #     # Check for MaxLengthValidator
    #     max_length = getattr(model_field, 'max_length', None)
    #     if not max_length:
    #         # Check if it's in validators
    #         max_length = next(
    #             (v.limit_value for v in model_field.validators if isinstance(v, MaxLengthValidator)),
    #             None,
    #         )
    #
    #     if max_length:
    #         attrs["maxlength"] = max_length
    #         # MaxLengthValidator should already be added by Django if max_length is set

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        return name

""" NEW """


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
    is_section = forms.BooleanField(
        label=_("Is Section"),
        initial=True,
        required=False,
        widget=forms.CheckboxInput()
    )

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
        }

    def clean(self):
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        is_section = cleaned_data.get('is_section')
        print("IS: ", is_section)
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
    class Meta:
        model = RecipeIngredient
        fields = ['name', 'quantity', 'unit']
        widgets = {
            'name': forms.TextInput(),
            'quantity': forms.NumberInput(attrs={
                'placeholder': '0',
                'min': '0.1',  # Add min attribute to match model validator
                'step': '0.1',  # Allow decimal values
            }),
            'unit': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set a default value for quantity to ensure it's always valid
        if not self.initial.get('quantity'):
            self.initial['quantity'] = 1.0

    def clean(self):
        cleaned_data = super().clean()
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
