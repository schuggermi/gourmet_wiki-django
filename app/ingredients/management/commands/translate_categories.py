from django.core.management.base import BaseCommand

from core.utils import translate_text
from ingredients.models import Category, CategoryTranslation


class Command(BaseCommand):
    help = "Translate all Category objects"

    def handle(self, *args, **kwargs):
        categories = Category.objects.all()

        if not categories.exists():
            self.stdout.write(self.style.WARNING("No Category entries found."))
            return

        self.stdout.write(f"Processing {categories.count()} ingredients...")

        for category in categories:
            translated_name = translate_text(category.name, "de")
            CategoryTranslation.objects.update_or_create(
                category=category,
                language_code="de",
                defaults={"name": translated_name},
            )

        self.stdout.write(self.style.SUCCESS("All Categories translated."))
