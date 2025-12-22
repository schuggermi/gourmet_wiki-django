from django.urls import path

from recipes import views


urlpatterns = [
    path('new/', views.recipe_create, name='recipe-new'),
    path('edit/<int:recipe_id>/', views.recipe_edit, name='recipe-edit'),
    path('edit/<int:recipe_id>/name-update/', views.recipe_name_update, name='recipe-name-update'),
    path('edit/<int:recipe_id>/details-update/', views.recipe_details_update, name='recipe-details-update'),

    path('edit/<int:recipe_id>/add_step/', views.step_add, name='step_add'),
    path('recipes/<int:recipe_id>/steps/reorder/', views.steps_reorder, name='steps_reorder'),
    path('recipes/<int:recipe_id>/steps/<int:step_id>/delete/', views.step_delete, name='step_delete'),

    path('edit/<int:recipe_id>/add_ingredient/', views.ingredient_add, name='ingredient_add'),
    path('edit/<int:recipe_id>/ingredients/<int:ingredient_id>/', views.ingredient_edit, name='ingredient_edit'),
    path('recipes/<int:recipe_id>/ingredients/cancel/', views.ingredient_cancel_edit, name='ingredient_cancel_edit'),
    path('recipes/<int:recipe_id>/ingredients/<int:ingredient_id>/delete/', views.ingredient_delete, name='ingredient_delete'),

    path('', views.RecipeListView.as_view(), name='recipe-list'),
    path('partial/', views.recipe_list_partial, name='recipe-list-partial'),
    path('create/', views.CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('<int:pk>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('favorite/<int:recipe_id>/', views.toggle_favorite, name='recipe-favorite'),
    path('rate/<int:recipe_id>/<int:score>/', views.rate_recipe, name='recipe-rate'),
    path('delete/<int:recipe_id>/', views.delete_recipe, name='recipe-delete'),
    #path('edit/<int:recipe_id>/', CreateRecipeWizardView.as_view(), name='recipe-edit'),
    path('add-image-form/', views.add_image_form, name='add_image_form'),
    path('<int:recipe_id>/calculate-scaled-ingredients/', views.get_calculate_scaled_ingredients,
         name='calculate_scaled_ingredients'),
]
