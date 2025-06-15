from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        default='users/avatars/avatar_placeholder.png',
        upload_to='users/avatars/',
        blank=True,
        null=True
    ) # TODO - consider using django_avatar library in future

    def __str__(self):
        return self.user.username
