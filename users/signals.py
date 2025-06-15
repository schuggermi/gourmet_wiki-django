from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from users.models import Profile

User = get_user_model()

@receiver(user_signed_up)
def create_profile_on_signup(sender, request, user, **kwargs):
    """Create profile specifically when user signs up via allauth"""
    Profile.objects.get_or_create(user=user)