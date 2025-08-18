# import time
# import random
# from pprint import pprint
#
# import requests
# from django.core.management.base import BaseCommand
# from django.db import transaction, IntegrityError
# from django.utils.text import slugify
# from ingredients.models import Ingredient, Nutrient, Category, IngredientNutrient, IngredientLookup
# from ingredients.usda_fdc import get_food_by_fdc_id
#
# # USDA suggests limiting requests per second to avoid 429s.
# # We'll space them out with base delay + jitter.
# BASE_DELAY = 0.5  # seconds
# MAX_RETRIES = 5
#
#
# class Command(BaseCommand):
#     help = "Seed the database with common ingredients using /food/<fdcId> endpoint."
#
#     def handle(self, *args, **kwargs):
#         lookups = IngredientLookup.objects.all()
#
#         if not lookups.exists():
#             self.stdout.write(self.style.WARNING("No IngredientLookup entries found."))
#             return
#
#         self.stdout.write(f"Processing {lookups.count()} ingredients from IngredientLookup...")
#
#         for lookup in lookups:
#             # Check by name (case-insensitive match)
#             if Ingredient.objects.filter(fdc_id=lookup.fdc_id).exists():
#                 self.stdout.write(self.style.WARNING(
#                     f"Skipping '{lookup.fdc_id}' — already exists by fdcId."
#                 ))
#                 continue
#
#             # Fetch from USDA API with retries & backoff
#             food_data = self.fetch_with_backoff(lookup.fdc_id)
#
#             if not food_data:
#                 self.stdout.write(self.style.ERROR(
#                     f"Failed to fetch data for FDC ID {lookup.fdc_id} ({lookup.description})"
#                 ))
#                 continue
#
#             self.create_or_update_ingredient(food_data)
#
#             # Delay to avoid hitting USDA rate limit
#             time.sleep(BASE_DELAY + random.uniform(0, 0.3))
#
#         self.stdout.write(self.style.SUCCESS("Finished processing ingredients."))
#
#     def fetch_with_backoff(self, fdc_id):
#         """Fetch a single food item with exponential backoff for 429s."""
#         for attempt in range(MAX_RETRIES):
#             try:
#                 return get_food_by_fdc_id(fdc_id)
#             except requests.exceptions.HTTPError as e:
#                 if e.response is not None and e.response.status_code == 429:
#                     delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.3)
#                     self.stdout.write(self.style.WARNING(
#                         f"Rate limited (429). Retrying FDC {fdc_id} in {delay:.2f}s..."
#                     ))
#                     time.sleep(delay)
#                 else:
#                     self.stdout.write(self.style.ERROR(
#                         f"HTTP error fetching FDC ID {fdc_id}: {e}"
#                     ))
#                     return None
#             except requests.exceptions.RequestException as e:
#                 delay = BASE_DELAY * (2 ** attempt)
#                 self.stdout.write(self.style.ERROR(
#                     f"Network error fetching FDC ID {fdc_id}: {e}. Retrying in {delay:.2f}s..."
#                 ))
#                 time.sleep(delay)
#         return None
#
#     def create_or_update_ingredient(self, ingredient_raw):
#         fdc_id = ingredient_raw['fdcId']
#         name = ingredient_raw['description']
#
#         # Category handling
#         category_obj = None
#         if 'foodCategory' in ingredient_raw:
#             category_obj, _ = Category.objects.get_or_create(
#                 wweia_fc_code=ingredient_raw['foodCategory']['code'] or None,
#                 name=ingredient_raw['foodCategory']['description'],
#                 defaults={
#                     'slug': slugify(ingredient_raw['foodCategory']['description']),
#                 }
#             )
#
#         # Ingredient creation
#         try:
#             with transaction.atomic():
#                 ingredient_obj, created = Ingredient.objects.get_or_create(
#                     slug=slugify(name),
#                     defaults={
#                         'fdc_id': fdc_id,
#                         'name': name,
#                         'slug': slugify(name),
#                         'category': category_obj,
#                     }
#                 )
#                 if created:
#                     self.stdout.write(self.style.SUCCESS(f"Created ingredient: {name}"))
#                 else:
#                     self.stdout.write(self.style.WARNING(f"Ingredient already exists: {name}"))
#         except IntegrityError:
#             ingredient_obj = Ingredient.objects.get(fdc_id=fdc_id)
#
#         # Nutrient linking
#         for nutrient_raw in ingredient_raw.get('foodNutrients', []):
#             nutrient_slug = slugify(nutrient_raw['nutrient']['name'])
#             nutrient_obj, _ = Nutrient.objects.get_or_create(
#                 slug=nutrient_slug,
#                 defaults={
#                     'fdc_nutrient_id': nutrient_raw['nutrient']['id'],
#                     'name': nutrient_raw['nutrient']['name'],
#                     'number': nutrient_raw['nutrient']['number'],
#                     'rank': nutrient_raw['nutrient']['rank'],
#                     'unit': nutrient_raw['nutrient']['unitName'],
#                 }
#             )
#
#             nutrient_amount = nutrient_raw.get('amount')
#             if nutrient_amount:
#                 IngredientNutrient.objects.get_or_create(
#                     ingredient=ingredient_obj,
#                     nutrient=nutrient_obj,
#                     defaults={'amount': nutrient_amount}
#                 )



import json
import time
import random
from pprint import pprint

import requests
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from django.utils import translation

from ingredients.models import (
    Ingredient,
    IngredientTranslation,
    Nutrient,
    IngredientNutrient,
    Category,
    CategoryTranslation,
)
from ingredients.usda_fdc import get_food_by_fdc_id

BASE_DELAY = 0.5  # seconds
MAX_RETRIES = 5


class Command(BaseCommand):
    help = "Import ingredients from a JSON file and enrich them via USDA FDC API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to the JSON file containing ingredients'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ingredients_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write(f"Processing {len(ingredients_data)} ingredients from JSON...")

        for entry in ingredients_data:
            fdc_id = entry.get('fdc_id')
            name_en = entry.get('name')
            name_de = entry.get('name_de')
            category_name_en = entry.get('category_name')
            category_name_de = entry.get('category_name_de')

            if not fdc_id or not name_en:
                self.stdout.write(self.style.WARNING("Skipping entry with missing fdc_id or name"))
                continue

            # Fetch USDA API data
            food_data = get_food_by_fdc_id(fdc_id, retries=MAX_RETRIES)
            if not food_data:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data for FDC {fdc_id}"))
                continue

            # Process category
            category_obj, _ = Category.objects.get_or_create(
                name=category_name_en,
                defaults={'slug': slugify(category_name_en)}
            )
            CategoryTranslation.objects.get_or_create(
                category=category_obj,
                language_code='de',
                defaults={'name': category_name_de or category_name_en}
            )

            # Process ingredient
            try:
                with transaction.atomic():
                    ingredient_obj, created = Ingredient.objects.get_or_create(
                        fdc_id=fdc_id,
                        defaults={
                            'name': name_en,
                            'slug': slugify(name_en),
                            'category': category_obj
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created ingredient: {name_en}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Ingredient exists: {name_en}"))

                    # Translations
                    IngredientTranslation.objects.get_or_create(
                        ingredient=ingredient_obj,
                        language_code='de',
                        defaults={'name': name_de or name_en}
                    )

                    # Nutrients
                    for nutrient_raw in food_data.get('foodNutrients', []):
                        nutrient_info = nutrient_raw.get('nutrient', {})
                        nutrient_slug = slugify(nutrient_info.get('name', ''))
                        if not nutrient_slug:
                            continue

                        nutrient_obj, _ = Nutrient.objects.get_or_create(
                            fdc_nutrient_id=nutrient_info.get('id'),
                            defaults={
                                'name': nutrient_info.get('name'),
                                'number': nutrient_info.get('number'),
                                'rank': nutrient_info.get('rank') or 0,
                                'unit': nutrient_info.get('unitName') or 'g',
                                'slug': nutrient_slug
                            }
                        )

                        amount = nutrient_raw.get('amount')
                        if amount is not None:
                            IngredientNutrient.objects.get_or_create(
                                ingredient=ingredient_obj,
                                nutrient=nutrient_obj,
                                defaults={'amount': amount}
                            )

            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"DB error for {name_en}: {e}"))

            # Avoid hitting USDA rate limits
            time.sleep(BASE_DELAY + random.uniform(0, 0.3))

        self.stdout.write(self.style.SUCCESS("Finished importing ingredients."))
