from django import forms

from menus.models import Menu


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'description', 'portions']
