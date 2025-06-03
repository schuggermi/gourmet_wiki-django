from django.core.management.base import BaseCommand

from ingredients.models import Ingredient

ingredients_seed = [
    {"name": "Sugar", "unit": "g", "price_per_unit": 0.002},
    {"name": "Flour", "unit": "g", "price_per_unit": 0.0015},
    {"name": "Milk", "unit": "ml", "price_per_unit": 0.0007},
    {"name": "Butter", "unit": "g", "price_per_unit": 0.012},
    {"name": "Egg", "unit": "piece", "price_per_unit": 0.35},
    {"name": "Salt", "unit": "g", "price_per_unit": 0.001},
    {"name": "Black Pepper", "unit": "g", "price_per_unit": 0.015},
    {"name": "Olive Oil", "unit": "ml", "price_per_unit": 0.01},
    {"name": "Onion", "unit": "g", "price_per_unit": 0.003},
    {"name": "Garlic", "unit": "g", "price_per_unit": 0.01},
    {"name": "Tomato", "unit": "g", "price_per_unit": 0.004},
    {"name": "Potato", "unit": "g", "price_per_unit": 0.001},
    {"name": "Carrot", "unit": "g", "price_per_unit": 0.002},
    {"name": "Chicken Breast", "unit": "g", "price_per_unit": 0.009},
    {"name": "Beef", "unit": "g", "price_per_unit": 0.012},
    {"name": "Pasta", "unit": "g", "price_per_unit": 0.002},
    {"name": "Rice", "unit": "g", "price_per_unit": 0.0015},
    {"name": "Cheese", "unit": "g", "price_per_unit": 0.01},
    {"name": "Cream", "unit": "ml", "price_per_unit": 0.005},
    {"name": "Basil", "unit": "g", "price_per_unit": 0.03},
    {"name": "Oregano", "unit": "g", "price_per_unit": 0.025},
    {"name": "Thyme", "unit": "g", "price_per_unit": 0.03},
    {"name": "Parsley", "unit": "g", "price_per_unit": 0.02},
    {"name": "Mushroom", "unit": "g", "price_per_unit": 0.006},
    {"name": "Bell Pepper", "unit": "g", "price_per_unit": 0.004},
    {"name": "Spinach", "unit": "g", "price_per_unit": 0.003},
    {"name": "Cucumber", "unit": "g", "price_per_unit": 0.002},
    {"name": "Lemon", "unit": "piece", "price_per_unit": 0.4},
    {"name": "Yogurt", "unit": "ml", "price_per_unit": 0.003},
    {"name": "Baking Powder", "unit": "g", "price_per_unit": 0.01},
]


class Command(BaseCommand):
    help = "Seed the database with common ingredients"

    def handle(self, *args, **kwargs):
        for data in ingredients_seed:
            Ingredient.objects.get_or_create(**data)

        self.stdout.write(self.style.SUCCESS("Successfully seeded ingredients."))
