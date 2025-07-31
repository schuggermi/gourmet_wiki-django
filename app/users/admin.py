from django.contrib import admin
from .models import Profile, UserBadge


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "points", "level")
    list_filter = ("role", "level")
    search_fields = ("user__username",)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("profile", "badge", "awarded_at")
