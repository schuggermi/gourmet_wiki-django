from pprint import pprint

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ingredients.models import Ingredient

from ingredients.usda_fdc import get_food_by_fdc_id

from ingredients.models import Nutrient, Category, IngredientNutrient

from ingredients.models import IngredientLookup


class Command(BaseCommand):
    help = "Seed the database with common ingredients"

    def handle(self, *args, **kwargs):
        for seed_data in IngredientLookup.objects.all():
            ingredient_raw = get_food_by_fdc_id(seed_data.fdc_id)

            if not ingredient_raw:
                self.stdout.write(self.style.ERROR(
                    f"Unable to find ingredient with fcId: {seed_data.fdc_id} ({seed_data.description})"))
                continue

            if 'wweiaFoodCategory' in ingredient_raw:
                category_raw = ingredient_raw['wweiaFoodCategory']
                category_obj, _ = Category.objects.update_or_create(
                    wweia_fc_code=category_raw['wweiaFoodCategoryCode'],
                    defaults={
                        'name': category_raw['wweiaFoodCategoryDescription'],
                        'slug': slugify(category_raw['wweiaFoodCategoryDescription']),
                    }
                )
            elif 'foodCategory' in ingredient_raw:
                category_raw = ingredient_raw['foodCategory']
                category_obj, _ = Category.objects.update_or_create(
                    wweia_fc_code=category_raw['code'],
                    defaults={
                        'name': category_raw['description'],
                        'slug': slugify(category_raw['description']),
                    }
                )

            ingredient_obj, _ = Ingredient.objects.update_or_create(
                fdc_id=ingredient_raw['fdcId'],
                defaults={
                    'name': ingredient_raw['description'],
                    'slug': slugify(ingredient_raw['description']),
                    'category': category_obj,
                }
            )

            for nutrient_raw in ingredient_raw['foodNutrients']:
                nutrient_obj, _ = Nutrient.objects.update_or_create(
                    slug=slugify(nutrient_raw['nutrient']['name']),
                    defaults={
                        'fdc_nutrient_id': slugify(nutrient_raw['nutrient']['id']),
                        'name': nutrient_raw['nutrient']['name'],
                        'number': nutrient_raw['nutrient']['number'],
                        'rank': nutrient_raw['nutrient']['rank'],
                        'unit': nutrient_raw['nutrient']['unitName'],
                    }
                )
                nutrient_amount = nutrient_raw.get('amount', 0)

                if nutrient_amount:
                    ingredient_nutrient_obj, _ = IngredientNutrient.objects.update_or_create(
                        ingredient=ingredient_obj,
                        nutrient=nutrient_obj,
                        defaults={
                            'amount': nutrient_raw['amount'],
                        }
                    )


            # pprint(ingredient_raw, indent=4)

        self.stdout.write(self.style.SUCCESS("Successfully seeded ingredients."))
