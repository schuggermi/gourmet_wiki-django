from decimal import Decimal


def calculate_recipe_cost(recipe):
    total = Decimal('0.00')
    for ri in recipe.ingredients.select_related('ingredient'):
        unit_price = ri.ingredient.price_per_unit
        quantity = ri.quantity
        total += unit_price * quantity
    return round(total, 2)
