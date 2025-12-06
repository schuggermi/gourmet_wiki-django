from django import forms
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.utils.translation import gettext_lazy as _

from recipes.forms import RecipeIngredientForm, RecipeImageForm, RecipePreparationStepForm
from recipes.models import RecipeIngredient, RecipeImage, RecipePreparationStep


class BaseRecipePreparationStepFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        # First pass: count valid non-deleted rows to preserve existing validation
        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            is_section = form.cleaned_data.get('is_section')
            section_title = form.cleaned_data.get('section_title')
            step_text = form.cleaned_data.get('step_text')

            if is_section:
                if section_title:
                    valid_forms += 1
            else:
                if step_text:
                    valid_forms += 1

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append(_("Preparation Steps must not be empty."))

        # Second pass: ensure every section has at least one non-section step beneath it
        # Build ordered list of active (non-deleted) forms by ORDER
        active_forms = [
            f for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get('DELETE')
        ]
        try:
            active_forms.sort(key=lambda f: f.cleaned_data.get('ORDER', 0))
        except Exception:
            # If ORDER is missing for some reason, keep current order
            pass

        n = len(active_forms)
        for idx, form in enumerate(active_forms):
            if not form.cleaned_data.get('is_section'):
                continue

            # Look ahead until next section or end to find at least one step
            has_step = False
            j = idx + 1
            while j < n:
                next_form = active_forms[j]
                if next_form.cleaned_data.get('is_section'):
                    break  # reached the next section without steps
                # non-section row counts as a step (it's already non-deleted)
                has_step = True
                break
                j += 1

            if not has_step:
                form.add_error('is_section', _("This section must contain at least one preparation step."))


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
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        ingredients = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            required_fields = [field_name for field_name, field in form.fields.items()
                               if field.required and field_name not in ('DELETE', 'id', 'ingredient')]

            all_required_filled = all(form.cleaned_data.get(fname) for fname in required_fields)

            if all_required_filled:
                valid_forms += 1

            # Check for ingredient_name instead of ingredient
            ingredient_name = form.cleaned_data.get('ingredient_name')
            if ingredient_name:
                ingredients.add(ingredient_name)

        if valid_forms == 0 and self.forms:
            self._non_form_errors.append("Add at least one ingredient.")


RecipeIngredientFormSet = modelformset_factory(
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
    extra=0,
    min_num=1,
    can_delete=True,
)


class BaseRecipeImageFormSet(BaseModelFormSet):
    # def clean(self):
    #     super().clean()
    #
    #     if any(self.errors):
    #         return
    #
    #     valid_forms = 0
    #     images = set()
    #     for form in self.forms:
    #         if form.cleaned_data and not form.cleaned_data.get('DELETE'):
    #             required_fields = [field_name for field_name, field in form.fields.items()
    #                                if field.required and field_name not in ('DELETE', )]
    #
    #             all_required_filled = all(form.cleaned_data.get(field_name) for field_name in required_fields)
    #
    #             if all_required_filled:
    #                 valid_forms += 1
    #
    #             image = form.cleaned_data.get('image')
    #             if image:
    #                 images.add(image)
    #
    #     if valid_forms == 0 and self.forms:
    #         self.non_form_errors().append("Images must not be empty.")

    def clean(self):
        super().clean()

        # stop if any form has validation errors already
        if any(self.errors):
            return

        valid_forms = 0
        images = set()

        for form in self.forms:
            # some guard rails
            if not hasattr(form, 'cleaned_data'):
                continue

            cd = form.cleaned_data
            # skip unsubmitted / marked-for-delete
            if not cd or cd.get('DELETE'):
                continue

            # required fields in this form (exclude Django's DELETE helper)
            required_fields = [
                fname for fname, f in form.fields.items()
                if f.required and fname != 'DELETE'
            ]

            # check whether each required field is filled *after* processing:
            # - prefer cleaned_data (new upload / new value)
            # - if cleaned_data doesn't contain a value, fall back to instance value
            # - if cleaned_data explicitly contains False (ClearableFileInput), treat as emptied
            all_required_filled = True
            for field_name in required_fields:
                value = cd.get(field_name, None)

                if value:
                    # has new value (e.g. uploaded file or other field)
                    continue

                # special-handling for file fields (image)
                field = form.fields[field_name]
                if isinstance(field, forms.FileField):
                    # if user explicitly cleared the file, cleaned_data[field_name] is False
                    if value is False:
                        all_required_filled = False
                        break
                    # otherwise, check the instance: existing file counts as filled
                    if getattr(form.instance, field_name, None):
                        continue
                    all_required_filled = False
                    break

                # non-file fields: fall back to instance value if present
                if getattr(form.instance, field_name, None):
                    continue

                all_required_filled = False
                break

            if all_required_filled:
                valid_forms += 1

            # collect image-like values that will actually exist after save
            img_val = cd.get('image', None)
            if img_val and img_val is not False:
                # new uploaded file
                images.add(img_val)
            else:
                # no new upload: if not explicitly cleared (img_val is not False)
                # and instance already has an image, count that
                if img_val is False:
                    # user cleared file — skip
                    pass
                else:
                    inst_img = getattr(form.instance, 'image', None)
                    if inst_img:
                        images.add(inst_img)

        # final validation
        if valid_forms == 0 and self.forms:
            # attach a non-form error (raising ValidationError will put it in non_form_errors)
            raise forms.ValidationError("Images must not be empty.")


RecipeImageFormSet = modelformset_factory(
    RecipeImage,
    form=RecipeImageForm,
    formset=BaseRecipeImageFormSet,
    extra=0,
    max_num=10,
    can_order=True,
    can_delete=True,
)
