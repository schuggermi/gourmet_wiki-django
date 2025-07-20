from django.urls import path

from menus.views import (
    MenuListView, MenuDetailView, CreateMenuWizardView, 
    add_menu_course_form, add_menu_item_form, get_recipes_by_course_type,
    menu_list_partial
)
from recipes.views import get_calculate_scaled_ingredients_menu

urlpatterns = [
    path('', MenuListView.as_view(), name='menu_list'),
    path('partial/', menu_list_partial, name='menu-list-partial'),
    path('create/', CreateMenuWizardView.as_view(), name='menu_create'),
    path('<int:pk>/', MenuDetailView.as_view(), name='menu_detail'),
    path('<int:menu_id>/calculate-scaled-ingredients-menu/', get_calculate_scaled_ingredients_menu,
         name='calculate_scaled_ingredients_menu'),
    path('add-menu-course-form/', add_menu_course_form, name='add_menu_course_form'),
    path('add-menu-item-form/', add_menu_item_form, name='add_menu_item_form'),
    path('get-recipes-by-course-type/', get_recipes_by_course_type, name='get_recipes_by_course_type'),
]
