from django import forms
from django.db.models import Q

from menus.models import Menu, MenuCourse, MenuItem
from recipes.models import Recipe


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description', 'portions']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Give your menu a name (e.g. Weekend Dinner Special)',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'cols': 40,
                    'placeholder': 'e.g. A curated selection of comforting dishes for a cozy weekend dinner.',
                }
            ),
        }


class MenuCourseForm(forms.ModelForm):
    ORDER = forms.IntegerField(required=False, widget=forms.HiddenInput())
    recipe = forms.ModelChoiceField(queryset=Recipe.objects.none(), required=True)

    class Meta:
        model = MenuCourse
        fields = ['course_type']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set recipe queryset based on user
        if user:
            recipe_queryset = Recipe.objects.filter(
                Q(created_by=user) | Q(favorite_by=user)
            ).distinct()

            # If course_type is already selected, filter recipes by course_type
            if self.instance and self.instance.pk and self.instance.course_type:
                recipe_queryset = recipe_queryset.filter(course_type=self.instance.course_type)
            elif self.data and self.prefix and f'{self.prefix}-course_type' in self.data:
                course_type = self.data.get(f'{self.prefix}-course_type')
                if course_type:
                    recipe_queryset = recipe_queryset.filter(course_type=course_type)
            else:
                # For new forms, filter by default course_type (MAIN)
                from recipes.models import CourseTypeChoice
                recipe_queryset = recipe_queryset.filter(course_type=CourseTypeChoice.MAIN)
                # Set initial value for course_type field
                self.initial['course_type'] = CourseTypeChoice.MAIN

            self.fields['recipe'].queryset = recipe_queryset

        for field_name in self.fields:
            if self.errors.get(field_name):
                old_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = (
                        old_class + ' border-3 border-red-400'
                )


class MenuItemForm(forms.ModelForm):
    ORDER = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = MenuItem
        fields = ['recipe']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter recipes to only show those created by or favorited by the user
        if user:
            self.fields['recipe'].queryset = Recipe.objects.filter(
                Q(created_by=user) | Q(favorite_by=user)
            ).distinct()

        for field_name in self.fields:
            if self.errors.get(field_name):
                old_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = (
                        old_class + ' border-3 border-red-400'
                )
