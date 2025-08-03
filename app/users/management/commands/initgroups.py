from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils.translation.trans_null import gettext_lazy as _


class Command(BaseCommand):
    help = 'Creates default user groups for role-based access'

    def handle(self, *args, **options):
        default_groups = [
            (_("Guest"), "Can read and browse content without login"),
            (_("Member"), "Can rate, comment, and save recipes"),
            (_("Author"), "Can submit recipes and create author profiles"),
            (_("Expert"), "Can publish articles, techniques, and tutorials"),
            (_("Curator"), "Can edit others' content, flag or mark for review"),
            (_("Moderator"), "Full access to content, approvals, and user management"),
        ]

        for name, description in default_groups:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created group: {name}'))
            else:
                self.stdout.write(f'ℹ️ Group already exists: {name}')
