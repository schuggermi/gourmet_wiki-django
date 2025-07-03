from django.urls import path

from menus.views import MenuListView, MenuDetailView, CreateMenuWizardView
from recipes.views import get_calculate_scaled_ingredients_menu

urlpatterns = [
    path('', MenuListView.as_view(), name='menu_list'),
    path('create/', CreateMenuWizardView.as_view(), name='menu_create'),
    path('<int:pk>/', MenuDetailView.as_view(), name='menu_detail'),
    path('<int:menu_id>/calculate-scaled-ingredients-menu/', get_calculate_scaled_ingredients_menu,
         name='calculate_scaled_ingredients_menu'),
]
