from decimal import Decimal

from django.template.defaultfilters import register

from recipes.models import RecipeIngredient


@register.filter
def calculate_quantity(ingredient: RecipeIngredient, target_portions: int):
    scale_factor = Decimal(target_portions / ingredient.recipe.portions)
    return ingredient.scale_quantity(scale_factor)
