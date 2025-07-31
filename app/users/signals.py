from allauth.account.signals import user_signed_up, email_confirmed
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from recipes.models import Recipe
from users.models import Profile, Badge

User = get_user_model()


@receiver(user_signed_up)
def create_profile_on_signup(sender, request, user, **kwargs):
    """Create profile specifically when user signs up via allauth"""
    Profile.objects.get_or_create(user=user)


@receiver(post_save, sender=Recipe)
def reward_recipe_submission(sender, instance, created, **kwargs):
    if created:
        profile = instance.created_by.profile
        profile.points += 25  # Points per Recipe
        profile.update_level()


@receiver(email_confirmed)
def award_member_badge_on_email_confirmed(request, email_address, **kwargs):
    user = email_address.user

    profile = getattr(user, 'profile', None)
    if profile:
        award_badge(profile, Badge.MEMBER)


def award_badge(profile, badge_name):
    from .models import UserBadge, Badge

    if badge_name not in Badge.values:
        raise ValueError(f"Unknown Badge: {badge_name}")

    user_badge, created = UserBadge.objects.get_or_create(profile=profile, badge=badge_name)
    return user_badge, created
