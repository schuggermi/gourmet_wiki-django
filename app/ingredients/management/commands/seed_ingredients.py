import time
import random
from pprint import pprint

import requests
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from ingredients.models import Ingredient, Nutrient, Category, IngredientNutrient, IngredientLookup
from ingredients.usda_fdc import get_food_by_fdc_id

# USDA suggests limiting requests per second to avoid 429s.
# We'll space them out with base delay + jitter.
BASE_DELAY = 0.5  # seconds
MAX_RETRIES = 5


class Command(BaseCommand):
    help = "Seed the database with common ingredients using /food/<fdcId> endpoint."

    def handle(self, *args, **kwargs):
        lookups = IngredientLookup.objects.all()

        if not lookups.exists():
            self.stdout.write(self.style.WARNING("No IngredientLookup entries found."))
            return

        self.stdout.write(f"Processing {lookups.count()} ingredients from IngredientLookup...")

        for lookup in lookups:
            # Check by name (case-insensitive match)
            if Ingredient.objects.filter(fdc_id=lookup.fdc_id).exists():
                self.stdout.write(self.style.WARNING(
                    f"Skipping '{lookup.fdc_id}' — already exists by fdcId."
                ))
                continue

            # Fetch from USDA API with retries & backoff
            food_data = self.fetch_with_backoff(lookup.fdc_id)

            if not food_data:
                self.stdout.write(self.style.ERROR(
                    f"Failed to fetch data for FDC ID {lookup.fdc_id} ({lookup.description})"
                ))
                continue

            self.create_or_update_ingredient(food_data)

            # Delay to avoid hitting USDA rate limit
            time.sleep(BASE_DELAY + random.uniform(0, 0.3))

        self.stdout.write(self.style.SUCCESS("Finished processing ingredients."))

    def fetch_with_backoff(self, fdc_id):
        """Fetch a single food item with exponential backoff for 429s."""
        for attempt in range(MAX_RETRIES):
            try:
                return get_food_by_fdc_id(fdc_id)
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.3)
                    self.stdout.write(self.style.WARNING(
                        f"Rate limited (429). Retrying FDC {fdc_id} in {delay:.2f}s..."
                    ))
                    time.sleep(delay)
                else:
                    self.stdout.write(self.style.ERROR(
                        f"HTTP error fetching FDC ID {fdc_id}: {e}"
                    ))
                    return None
            except requests.exceptions.RequestException as e:
                delay = BASE_DELAY * (2 ** attempt)
                self.stdout.write(self.style.ERROR(
                    f"Network error fetching FDC ID {fdc_id}: {e}. Retrying in {delay:.2f}s..."
                ))
                time.sleep(delay)
        return None

    def create_or_update_ingredient(self, ingredient_raw):
        fdc_id = ingredient_raw['fdcId']
        name = ingredient_raw['description']

        # Category handling
        category_obj = None
        # if 'wweiaFoodCategory' in ingredient_raw:
        #     category_raw = ingredient_raw['wweiaFoodCategory']
        #     print("CATEGORY RAW: ", category_raw)
        #     category_obj, _ = Category.objects.get_or_create(
        #         wweia_fc_code=category_raw['wweiaFoodCategoryCode'],
        #         name=category_raw['wweiaFoodCategoryDescription'],
        #         defaults={
        #             'slug': slugify(category_raw['wweiaFoodCategoryDescription']),
        #         }
        #     )
        # elif
        if 'foodCategory' in ingredient_raw:
            # print("FOOD CATEGORY: ", ingredient_raw['foodCategory'])
            category_obj, _ = Category.objects.get_or_create(
                wweia_fc_code=ingredient_raw['foodCategory']['code'] or None,
                name=ingredient_raw['foodCategory']['description'],
                defaults={
                    'slug': slugify(ingredient_raw['foodCategory']['description']),
                }
            )

        # Ingredient creation
        try:
            with transaction.atomic():
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    slug=slugify(name),
                    defaults={
                        'fdc_id': fdc_id,
                        'name': name,
                        'slug': slugify(name),
                        'category': category_obj,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created ingredient: {name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Ingredient already exists: {name}"))
        except IntegrityError:
            ingredient_obj = Ingredient.objects.get(fdc_id=fdc_id)

        # Nutrient linking
        for nutrient_raw in ingredient_raw.get('foodNutrients', []):
            nutrient_slug = slugify(nutrient_raw['nutrient']['name'])
            nutrient_obj, _ = Nutrient.objects.get_or_create(
                slug=nutrient_slug,
                defaults={
                    'fdc_nutrient_id': nutrient_raw['nutrient']['id'],
                    'name': nutrient_raw['nutrient']['name'],
                    'number': nutrient_raw['nutrient']['number'],
                    'rank': nutrient_raw['nutrient']['rank'],
                    'unit': nutrient_raw['nutrient']['unitName'],
                }
            )

            nutrient_amount = nutrient_raw.get('amount')
            if nutrient_amount:
                IngredientNutrient.objects.get_or_create(
                    ingredient=ingredient_obj,
                    nutrient=nutrient_obj,
                    defaults={'amount': nutrient_amount}
                )
