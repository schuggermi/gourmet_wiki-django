from django.urls import path

from recipes.views import RecipeListView, CreateRecipeWizardView, add_ingredient_form, add_image_form, \
    add_preparation_step_form

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('create/', CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('add-preparation_step-form/', add_preparation_step_form, name='add_preparation_step_form'),
    path('add-ingredient-form/', add_ingredient_form, name='add_ingredient_form'),
    path('add-image-form/', add_image_form, name='add_image_form'),
]
