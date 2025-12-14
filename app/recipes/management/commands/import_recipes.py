import json
import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from recipes.models import Recipe, RecipeIngredient, RecipePreparationStep

User = get_user_model()

def remove_comments(json_string):
    """
    Remove C-style comments from a JSON string.
    This allows for comments in the JSON file which are not valid in standard JSON.
    """
    # Remove single line comments (//...)
    json_string = re.sub(r'//.*?\n', '\n', json_string)
    # Remove multi-line comments (/* ... */)
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

        # Check if file exists
        if not os.path.exists(json_file_path):
            raise CommandError(f'File {json_file_path} does not exist')

        # Get the user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

        # Read and parse the JSON file
        try:
            with open(json_file_path, 'r') as file:
                json_content = file.read()
                # Remove comments from the JSON content
                json_content = remove_comments(json_content)
                recipes_data = json.loads(json_content)
        except json.JSONDecodeError:
            raise CommandError(f'Invalid JSON in file {json_file_path}')

        recipes_created = 0
        ingredients_created = 0
        steps_created = 0

        # Process each recipe
        for recipe_data in recipes_data:
            try:
                # Create the recipe
                recipe = Recipe.objects.create(
                    name=recipe_data.get('name', ''),
                    description=recipe_data.get('description', ''),
                    created_by=user,
                    course_type=recipe_data.get('course_type', 'main'),
                    portions=recipe_data.get('portions', 4),
                    working_time_hours=recipe_data.get('working_time_hours', 0),
                    working_time_minutes=recipe_data.get('working_time_minutes', 0),
                    cooking_time_minutes=recipe_data.get('cooking_time_minutes', 0),
                    rest_time_hours=recipe_data.get('rest_time_hours', 0),
                    rest_time_minutes=recipe_data.get('rest_time_minutes', 0),
                    skill_level=recipe_data.get('skill_level', 'Beginner'),
                    is_published=True
                )
                recipes_created += 1

                # Create ingredients
                # Keep track of ingredients to avoid duplicates
                added_ingredients = set()
                for i, ingredient_data in enumerate(recipe_data.get('ingredients', [])):
                    ingredient_name = ingredient_data.get('ingredient', '')
                    # Skip empty ingredient names or duplicates
                    if not ingredient_name or ingredient_name in added_ingredients:
                        continue

                    # Add to set to track duplicates
                    added_ingredients.add(ingredient_name)

                    # Ensure unit is not empty
                    unit = ingredient_data.get('unit', '')
                    if not unit:
                        unit = 'g'  # Default to gram if unit is not specified

                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient_name,
                        quantity=ingredient_data.get('quantity', 0),
                        unit=unit
                    )
                    ingredients_created += 1

                # Create preparation steps
                for step_data in recipe_data.get('steps', []):
                    RecipePreparationStep.objects.create(
                        recipe=recipe,
                        step_text=step_data.get('step_text', ''),
                        order=step_data.get('order', 0)
                    )
                    steps_created += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating recipe: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {recipes_created} recipes with {ingredients_created} ingredients and {steps_created} preparation steps'))
