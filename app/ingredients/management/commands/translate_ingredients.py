from django.core.management.base import BaseCommand

from core.utils import translate_text
from ingredients.models import Ingredient, IngredientTranslation


class Command(BaseCommand):
    help = "Translate all Ingredient objects"

    def handle(self, *args, **kwargs):
        ingredients = Ingredient.objects.all()

        if not ingredients.exists():
            self.stdout.write(self.style.WARNING("No Ingredient entries found."))
            return

        self.stdout.write(f"Processing {ingredients.count()} ingredients...")

        for ingredient in ingredients:
            translated_name = translate_text(ingredient.name, "de")
            IngredientTranslation.objects.update_or_create(
                ingredient=ingredient,
                language_code="de",
                defaults={"name": translated_name},
            )

        self.stdout.write(self.style.SUCCESS("All Ingredients translated."))
