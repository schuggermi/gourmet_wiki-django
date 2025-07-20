from decimal import Decimal


def calculate_recipe_cost(recipe):
    total = Decimal('0.00')
    for ri in recipe.ingredients.all():
        unit_price = ri.price_per_unit
        quantity = ri.quantity
        total += unit_price * quantity
    return round(total, 2)
