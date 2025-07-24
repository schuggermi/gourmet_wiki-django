from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

User = get_user_model()


class SkillLevelChoice(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    PROFESSIONAL = 'professional', _('Professional')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        default='users/avatars/avatar_placeholder.png',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )  # TODO - consider using django_avatar library in future
    skill_level = models.CharField(
        max_length=50,
        choices=SkillLevelChoice.choices,
        default=SkillLevelChoice.BEGINNER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
