from django.shortcuts import get_object_or_404

from menus.models import Menu


def calculate_scaled_ingredients_menu(menu_id: int, target_portions: int):
    menu = get_object_or_404(Menu, id=menu_id)
    menu_items = menu.items.all()
    context = {
        'menu': menu,
        'portions': target_portions,
        'ingredients': {}
    }

    for menu_item in menu_items:
        recipe = menu_item.recipe
        recipe_id = menu_item.menu_course.order
        context["ingredients"][recipe_id] = recipe.calculate_scaled_ingredients(target_portions or menu.portions)

    return context