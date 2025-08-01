from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Creates default user groups for role-based access'

    def handle(self, *args, **options):
        default_groups = [
            ("Guest", "Can read and browse content without login"),
            ("Member", "Can rate, comment, and save recipes"),
            ("Author", "Can submit recipes and create author profiles"),
            ("Expert", "Can publish articles, techniques, and tutorials"),
            ("Curator", "Can edit others' content, flag or mark for review"),
            ("Moderator", "Full access to content, approvals, and user management"),
        ]

        for name, description in default_groups:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Created group: {name}'))
            else:
                self.stdout.write(f'ℹ️ Group already exists: {name}')
