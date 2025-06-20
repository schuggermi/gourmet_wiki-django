from pprint import pprint

from django import forms
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import modelformset_factory, BaseModelFormSet

from recipes.forms import RecipeIngredientForm, RecipeImageForm, RecipePreparationStepForm
from recipes.models import RecipeIngredient, RecipeImage, RecipePreparationStep


class BaseRecipePreparationStepFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        prep_steps = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                required_fields = [field_name for field_name, field in form.fields.items()
                                   if field.required and field_name != 'DELETE' and field_name not in ('order', 'id')]

                all_required_filled = all(form.cleaned_data.get(field_name) for field_name in required_fields)

                if all_required_filled:
                    valid_forms += 1

                prep_step = form.cleaned_data.get('step_text')
                if prep_step:
                    prep_steps.add(prep_step)

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append("Preparation Steps must not be empty.")


RecipePreparationStepFormSet = modelformset_factory(
    RecipePreparationStep,
    form=RecipePreparationStepForm,
    formset=BaseRecipePreparationStepFormSet,
    extra=0,
    min_num=1,
    can_order=True,
    can_delete=True,
)


class BaseRecipeIngredientFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()  # MUST call this first!

        if any(self.errors):
            # If there are errors, skip further validation
            return

        valid_forms = 0
        images = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            # If the form is marked for deletion, skip it for validation/counting
            if form.cleaned_data.get('DELETE'):
                continue

            # Identify required fields excluding 'DELETE', 'order', 'id'
            required_fields = [
                fname for fname, field in form.fields.items()
                if field.required and fname not in ('DELETE', 'order', 'id')
            ]

            # Check all required fields are filled
            all_required_filled = all(form.cleaned_data.get(fname) for fname in required_fields)

            if all_required_filled:
                valid_forms += 1

            # Collect images for further processing if needed
            image = form.cleaned_data.get('image')
            if image:
                images.add(image)

        if valid_forms == 0 and self.forms:
            # Add a non-field error if no valid forms remain (after deletion)
            self._non_form_errors.append("Images must not be empty.")


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
    extra=0,
    min_num=1,
    can_delete=True,
)


class BaseRecipeImageFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        images = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                required_fields = [field_name for field_name, field in form.fields.items()
                                   if field.required and field_name != 'DELETE' and field_name not in ('order', 'id')]

                print(f"{required_fields=}")

                all_required_filled = all(form.cleaned_data.get(field_name) for field_name in required_fields)

                if all_required_filled:
                    valid_forms += 1

                image = form.cleaned_data.get('image')
                if image:
                    images.add(image)

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append("Images must not be empty.")


RecipeImageFormSet = modelformset_factory(
    RecipeImage,
    form=RecipeImageForm,
    formset=BaseRecipeImageFormSet,
    extra=0,
    max_num=10,
    can_order=True,
    can_delete=True,
)
