from django.urls import path

from core.views import signup_disabled

urlpatterns = [
    path("accounts/signup/", signup_disabled, name="account_signup"),
]
