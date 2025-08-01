from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

User = get_user_model()


class SkillLevelChoice(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    PROFESSIONAL = 'professional', _('Professional')


from django.utils.translation import gettext_lazy as _


class UserLevelChoice(models.TextChoices):
    LEVEL_1 = '1', _('Kitchen Newbie')
    LEVEL_2 = '2', _('Recipe Explorer')
    LEVEL_3 = '3', _('Kitchen Connoisseur')
    LEVEL_4 = '4', _('Knowledge Contributor')
    LEVEL_5 = '5', _('Community Pioneer')
    LEVEL_6 = '6', _('Professional Author')
    LEVEL_7 = '7', _('Kitchen Mentor')
    LEVEL_8 = '8', _('Gourmet Master')

    @classmethod
    def get_next_level(cls, current_level):
        try:
            idx = list(cls).index(cls(current_level))
            return list(cls)[idx + 1] if idx + 1 < len(cls) else None
        except ValueError:
            return None


LEVEL_DESCRIPTIONS = {
    1: _("Entry into the platform"),
    2: _("First own contributions"),
    3: _("Contributions with added value"),
    4: _("Strong professional contribution"),
    5: _("High activity & quality"),
    6: _("Recognized professional profile"),
    7: _("Actively supports others"),
    8: _("Represents the platform"),
}


class UserRole(models.TextChoices):
    GUEST = 'guest', _('Guest')
    MEMBER = 'member', _('Member')
    AUTHOR = 'author', _('Author')
    EXPERT = 'expert', _('Expert')
    CURATOR = 'curator', _('Curator')
    ADMIN = 'admin', _('Admin')


# class UserLevelChoice(models.TextChoices):
#     LEVEL_1 = '1', _('Küchenneuling')
#     LEVEL_2 = '2', _('Rezeptentdecker:in')
#     LEVEL_3 = '3', _('Küchenkenner:in')
#     LEVEL_4 = '4', _('Wissensstifter:in')
#     LEVEL_5 = '5', _('Community-Vorreiter:in')
#     LEVEL_6 = '6', _('Fachautor:in')
#     LEVEL_7 = '7', _('Küchenmentor:in')
#     LEVEL_8 = '8', _('GourmetMaster:in')
#
#     @classmethod
#     def get_next_level(cls, current_level):
#         try:
#             idx = list(cls).index(cls(current_level))
#             return list(cls)[idx + 1] if idx + 1 < len(cls) else None
#         except ValueError:
#             return None
#
#
# LEVEL_DESCRIPTIONS = {
#     1: _("Einstieg in die Plattform"),
#     2: _("Erste eigene Inhalte"),
#     3: _("Beiträge mit Mehrwert"),
#     4: _("Starker fachlicher Beitrag"),
#     5: _("Hohe Aktivität & Qualität"),
#     6: _("Anerkanntes Fachprofil"),
#     7: _("Unterstützt andere aktiv"),
#     8: _("Repräsentiert die Plattform"),
# }
#
#
# class UserRole(models.TextChoices):
#     GUEST = 'guest', _('Gast')
#     MEMBER = 'member', _('Mitglied')
#     AUTHOR = 'author', _('Autor:in')
#     EXPERT = 'expert', _('Expert:in')
#     CURATOR = 'curator', _('Kurator:in')
#     ADMIN = 'admin', _('Admin')


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
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.MEMBER,
    )
    points = models.PositiveIntegerField(default=0)
    level = models.CharField(
        max_length=50,
        choices=UserLevelChoice.choices,
        default=UserLevelChoice.LEVEL_1,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def max_points_to_next_level(self):
        if self.points < 50:
            return 50
        elif self.points < 150:
            return 150
        elif self.points < 300:
            return 300
        elif self.points < 500:
            return 500
        elif self.points < 800:
            return 800
        elif self.points < 1200:
            return 1200
        elif self.points < 2000:
            return 2000
        else:
            return None

    @property
    def missing_points_to_next_level(self):
        if self.points < 50:
            return 50 - self.points
        elif self.points < 150:
            return 150 - self.points
        elif self.points < 300:
            return 300 - self.points
        elif self.points < 500:
            return 500 - self.points
        elif self.points < 800:
            return 800 - self.points
        elif self.points < 1200:
            return 1200 - self.points
        elif self.points < 2000:
            return 2000 - self.points
        else:
            return 0  # Max level reached

    def update_level(self):
        if self.points < 50:
            self.level = 1
        elif self.points < 150:
            self.level = 2
        elif self.points < 300:
            self.level = 3
        elif self.points < 500:
            self.level = 4
        elif self.points < 800:
            self.level = 5
        elif self.points < 1200:
            self.level = 6
        elif self.points < 2000:
            self.level = 7
        else:
            self.level = 8
        self.save()

    def get_next_level_display_name(self):
        next_level = UserLevelChoice.get_next_level(self.level)
        return next_level.label if next_level else None

    def get_next_level_description(self):
        next_level_num = self.level + 1
        return LEVEL_DESCRIPTIONS.get(next_level_num)


class Badge(models.TextChoices):
    MEMBER = 'member', 'Member'


BADGE_DESCRIPTIONS = {
    Badge.MEMBER: "Joined as a Community Member",
}


class UserBadge(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='badges')
    badge = models.CharField(max_length=30, choices=Badge.choices)
    awarded_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'badge')

    def __str__(self):
        return f"{self.get_badge_display()} since {self.awarded_at.strftime('%d.%m.%Y')}"

    @property
    def description(self):
        return BADGE_DESCRIPTIONS.get(self.badge, "")
