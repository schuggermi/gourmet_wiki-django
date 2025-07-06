from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet

from menus.forms import MenuCourseForm, MenuItemForm
from menus.models import MenuCourse, MenuItem


class BaseMenuCourseFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        course_types = set()
        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            required_fields = [field_name for field_name, field in form.fields.items()
                               if field.required and field_name not in ('DELETE',)]

            all_required_filled = all(form.cleaned_data.get(fname) for fname in required_fields)

            if all_required_filled:
                valid_forms += 1

            course_type = form.cleaned_data.get('course_type')
            if course_type:
                if course_type in course_types:
                    form.add_error('course_type', 'This course type is already used.')
                course_types.add(course_type)

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append("Menu Courses must not be empty.")


class BaseMenuItemFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        valid_forms = 0
        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get('DELETE'):
                continue

            required_fields = [field_name for field_name, field in form.fields.items()
                               if field.required and field_name not in ('DELETE',)]

            all_required_filled = all(form.cleaned_data.get(fname) for fname in required_fields)

            if all_required_filled:
                valid_forms += 1

        if valid_forms == 0 and self.forms:
            self.non_form_errors().append("Menu Items must not be empty.")


MenuCourseFormSet = modelformset_factory(
    MenuCourse,
    form=MenuCourseForm,
    formset=BaseMenuCourseFormSet,
    extra=0,
    min_num=1,
    can_order=True,
    can_delete=True,
)

MenuItemFormSet = modelformset_factory(
    MenuItem,
    form=MenuItemForm,
    formset=BaseMenuItemFormSet,
    extra=0,
    min_num=1,
    can_order=True,
    can_delete=True,
)
