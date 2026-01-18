import json
import os
import re
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeIngredient, RecipePreparationStep
from ingredients.models import Ingredient  # Import des Ingredients-Modells

User = get_user_model()

def remove_comments(json_string):
    json_string = re.sub(r'//.*?\n', '\n', json_string)
    json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)
    return json_string

class Command(BaseCommand):
    help = 'Imports recipes from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing recipes')
        parser.add_argument('--user', type=str, help='Username of the user to assign as creator of the recipes', default='admin')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        username = options['user']

        if not os.path.exists(json_file_path):
            raise CommandError(f'File {json_file_path} does not exist')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

        try:
            with open(json_file_path, 'r') as file:
                json_content = remove_comments(file.read())
                recipes_data = json.loads(json_content)
        except json.JSONDecodeError:
            raise CommandError(f'Invalid JSON in file {json_file_path}')

        recipes_created = 0
        ingredients_created = 0
        steps_created = 0

        for recipe_data in recipes_data:
            try:
                # Recipe erstellen
                recipe = Recipe.objects.create(
                    name=recipe_data.get('name', ''),
                    description=recipe_data.get('description', ''),
                    author=user,
                    course_type=recipe_data.get('course_type', 'main'),
                    portions=recipe_data.get('portions', 4),
                    cooking_time_minutes=recipe_data.get('cooking_time_minutes', 30),
                    skill_level=recipe_data.get('skill_level', 'Beginner'),
                    is_published=True
                )
                recipes_created += 1

                # Zutaten erstellen
                added_ingredients = set()
                for ingredient_data in recipe_data.get('ingredients', []):
                    ingredient_name = ingredient_data.get('ingredient', '').strip()
                    if not ingredient_name or ingredient_name in added_ingredients:
                        continue
                    added_ingredients.add(ingredient_name)

                    # Ingredient-Objekt holen oder erstellen
                    ingredient_obj, _ = Ingredient.objects.get_or_create(name=ingredient_name)

                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient_obj,
                        quantity=Decimal(ingredient_data.get('quantity', 0)),
                        unit=ingredient_data.get('unit', 'g'),
                        price_per_unit=Decimal(ingredient_data.get('price_per_unit', 0))
                    )
                    ingredients_created += 1

                # Zubereitungsschritte erstellen
                for step_data in recipe_data.get('steps', []):
                    RecipePreparationStep.objects.create(
                        recipe=recipe,
                        step_text=step_data.get('step_text', ''),
                        order=step_data.get('order', 0),
                        is_section=step_data.get('is_section', False),
                        section_title=step_data.get('section_title', '')
                    )
                    steps_created += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating recipe "{recipe_data.get("name", "")}": {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported {recipes_created} recipes with {ingredients_created} ingredients and {steps_created} preparation steps'
        ))

