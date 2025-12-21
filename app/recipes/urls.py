from django.urls import path

from recipes.views import RecipeListView, CreateRecipeWizardView, add_image_form, RecipeDetailView, get_calculate_scaled_ingredients, toggle_favorite, rate_recipe, \
    recipe_list_partial, delete_recipe, recipe_create, recipe_edit, step_add, ingredient_add, recipe_name_update, recipe_details_update


urlpatterns = [
    path('new/', recipe_create, name='recipe-new'),
    path('edit/<int:recipe_id>/', recipe_edit, name='recipe-edit'),
    path('edit/<int:recipe_id>/name-update/', recipe_name_update, name='recipe-name-update'),
    path('edit/<int:recipe_id>/details-update/', recipe_details_update, name='recipe-details-update'),
    path('edit/<int:recipe_id>/add_step/', step_add, name='step_add'),
    path('edit/<int:recipe_id>/add_ingredient/', ingredient_add, name='ingredient_add'),

    path('', RecipeListView.as_view(), name='recipe-list'),
    path('partial/', recipe_list_partial, name='recipe-list-partial'),
    path('create/', CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('favorite/<int:recipe_id>/', toggle_favorite, name='recipe-favorite'),
    path('rate/<int:recipe_id>/<int:score>/', rate_recipe, name='recipe-rate'),
    path('delete/<int:recipe_id>/', delete_recipe, name='recipe-delete'),
    #path('edit/<int:recipe_id>/', CreateRecipeWizardView.as_view(), name='recipe-edit'),
    path('add-image-form/', add_image_form, name='add_image_form'),
    path('<int:recipe_id>/calculate-scaled-ingredients/', get_calculate_scaled_ingredients,
         name='calculate_scaled_ingredients'),
]
