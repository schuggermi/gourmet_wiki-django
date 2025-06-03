from django.urls import path

from recipes.views import RecipeListView, CreateRecipeWizardView, add_ingredient_form

urlpatterns = [
    path('', RecipeListView.as_view(), name='recipe-list'),
    path('create/', CreateRecipeWizardView.as_view(), name='recipe-create'),
    path('add-ingredient-form/', add_ingredient_form, name='add_ingredient_form'),

]
