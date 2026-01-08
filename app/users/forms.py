from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=User._meta.get_field('first_name').max_length,
        label=User._meta.get_field('first_name').verbose_name,
        widget=forms.TextInput(attrs={
            'placeholder': 'Paul',
        })
    )
    last_name = forms.CharField(
        max_length=User._meta.get_field('last_name').max_length,
        label=User._meta.get_field('last_name').verbose_name,
        widget=forms.TextInput(attrs={
            'placeholder': 'Bocuse',
        })
    )
    email = forms.EmailField(
        max_length=User._meta.get_field('email').max_length,
        label=User._meta.get_field('email').verbose_name,
        widget=forms.TextInput(attrs={
            'placeholder': 'paul.bocuse@example.com',
        })
    )
    username = forms.CharField(
        max_length=User._meta.get_field('username').max_length,
        label=User._meta.get_field('username').verbose_name,
        widget=forms.TextInput(attrs={
            'placeholder': 'paul.bocuse',
        })
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
