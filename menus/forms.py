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
