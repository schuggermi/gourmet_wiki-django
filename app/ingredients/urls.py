from django.urls import path

from ingredients.api.views import IngredientLookupSearchView
from ingredients.views import ingredient_lookup_options

app_name = 'ingredients'

urlpatterns = [
    path('api/ingredient-lookup/', IngredientLookupSearchView.as_view(), name='ingredient-lookup-search'),
    path('ingredient-options/', ingredient_lookup_options, name='ingredient-options'),
]
