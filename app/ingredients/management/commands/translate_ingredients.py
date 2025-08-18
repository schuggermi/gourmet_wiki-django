import json

from django.core.management.base import BaseCommand

# from core.utils import translate_text
from ingredients.models import Ingredient, IngredientTranslation
from langchain_core.prompts import PromptTemplate

from core.ollama import use_ollama


class Command(BaseCommand):
    help = "Translate all Ingredient objects"

    def handle(self, *args, **kwargs):
        ingredients = Ingredient.objects.all()

        if not ingredients.exists():
            self.stdout.write(self.style.WARNING("No Ingredient entries found."))
            return

        self.stdout.write(f"Processing {ingredients.count()} ingredients...")

        for ingredient in ingredients:
            if ingredient.id in IngredientTranslation.objects.all().values_list('ingredient_id', flat=True):
                continue

            print("ING NAME: ", ingredient.name)

            prompt = PromptTemplate(
                input_variables=["ingredient", "language"],
                template=
                """
                Translate the food recipe ingredient '{ingredient}' into {language}.
                
                Instructions:
                1. Always translate the main ingredient using the correct culinary term in {language}. 
                   Examples:
                   - 'Venison' → 'Hirschfleisch'
                   - 'Beef' → 'Rindfleisch'
                   - 'Chicken' → 'Hähnchen'
                2. Translate all descriptive words, states, or preparation notes (e.g., 'raw', 'fresh', 'organic', 'exposed to ultraviolet light') into correct {language} culinary terms.
                   Examples:
                   - 'Raw' → 'Roh'
                   - 'Fresh' → 'Frisch'
                   - 'Exposed to ultraviolet light' → 'UV-bestrahlt'
                3. For geographical origins (countries, cities, regions):
                   - Translate into {language} if a standard German name exists.
                   - Otherwise, keep the original name.
                4. Combine all parts into a **natural German culinary phrase**, following this style:
                   - "Venison Sitka Raw Alaska Native" → "Rohes Hirschfleisch aus Sitka, Alaska, von Ureinwohnern"
                   - "Mushrooms, portabella, exposed to ultraviolet light, raw" → "Rohe Portabella-Pilze (UV-bestrahlt)"
                5. Return ONLY a JSON object in this format: {{"translated": "translated text"}}
                6. Do not include explanations, extra text, or formatting.
                7. Never make mistakes like confusing 'Venison' with 'Wildschwein'.
                8. Always focus on clarity, correctness, and usability in a **recipe context**.
                """
            )
            data = {
                "ingredient": ingredient.name.replace('"', "'"),
                "language": "german",
            }

            response: str = use_ollama(prompt, data)
            print("RESPONSE: ", response)
            translated_name: json = json.loads(response.strip())
            if translated_name.get('translated'):
                IngredientTranslation.objects.update_or_create(
                    ingredient=ingredient,
                    language_code="de",
                    defaults={"name": translated_name.get('translated')},
                )
            else:
                self.stdout.write(self.style.WARNING("Missing translated ingredient."))
                continue

        self.stdout.write(self.style.SUCCESS("All Ingredients translated."))
