from django.urls import path

from recipes.views import RecipeListView, CreateRecipeWizardView, add_ingredient_form, add_image_form, \
    add_preparation_step_form, RecipeDetailView, get_calculate_scaled_ingredients, toggle_favorite, rate_recipe, \
    recipe_list_partial, delete_recipe

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('partial/', recipe_list_partial, name='recipe-list-partial'),
    path('create/', CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('favorite/<int:recipe_id>/', toggle_favorite, name='recipe-favorite'),
    path('rate/<int:recipe_id>/<int:score>/', rate_recipe, name='recipe-rate'),
    path('delete/<int:recipe_id>/', delete_recipe, name='recipe-delete'),
    path('edit/<int:recipe_id>/', CreateRecipeWizardView.as_view(), name='recipe-edit'),
    path('add-preparation_step-form/', add_preparation_step_form, name='add_preparation_step_form'),
    path('add-ingredient-form/', add_ingredient_form, name='add_ingredient_form'),
    path('add-image-form/', add_image_form, name='add_image_form'),
    path('<int:recipe_id>/calculate-scaled-ingredients/', get_calculate_scaled_ingredients,
         name='calculate_scaled_ingredients'),
]
