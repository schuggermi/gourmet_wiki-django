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
                                   if field.required and field_name != 'DELETE' and field_name != 'order']

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
    validate_min=True,
    validate_max=True,
    max_num=50,
    can_order=True,
    can_delete=False,
)


class BaseRecipeIngredientFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        ingredients = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                # Get all required fields from the form
                required_fields = [field_name for field_name, field in form.fields.items()
                                   if field.required and field_name != 'DELETE']

                # Check if all required fields are filled
                all_required_filled = all(form.cleaned_data.get(field_name) for field_name in required_fields)

                if all_required_filled:
                    valid_forms += 1

                # Check for duplicated ingredient
                ingredient = form.cleaned_data.get('ingredient')
                if ingredient in ingredients:
                    form.add_error('ingredient', 'Duplicated ingredient.')
                if ingredient:
                    ingredients.add(ingredient)

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append("Ingredients must not be empty.")


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
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
                                   if field.required and field_name != 'DELETE' and field_name != 'order']

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
    min_num=0,
    max_num=10,
    validate_min=True,
    validate_max=True,
    can_order=True,
    can_delete=False,
)
