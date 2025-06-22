from django.urls import path

from recipes.views import RecipeListView, CreateRecipeWizardView, add_ingredient_form, add_image_form, \
    add_preparation_step_form, RecipeDetailView, get_calculate_scaled_ingredients

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('create/', CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('edit/<int:recipe_id>/', CreateRecipeWizardView.as_view(), name='recipe-edit'),
    path('add-preparation_step-form/', add_preparation_step_form, name='add_preparation_step_form'),
    path('add-ingredient-form/', add_ingredient_form, name='add_ingredient_form'),
    path('add-image-form/', add_image_form, name='add_image_form'),
    path('<int:recipe_id>/calculate-scaled-ingredients/', get_calculate_scaled_ingredients, name='calculate_scaled_ingredients'),
]
