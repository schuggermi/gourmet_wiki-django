from django.core.management.base import BaseCommand

from ingredients.models import Ingredient

ingredients_seed = [
    {"fdcId": 123, "description": "Test", "foodCategoryId": 123},
]


class Command(BaseCommand):
    help = "Seed the database with common ingredients"

    def handle(self, *args, **kwargs):
        for data in ingredients_seed:
            Ingredient.objects.get_or_create(**data)

        self.stdout.write(self.style.SUCCESS("Successfully seeded ingredients."))
