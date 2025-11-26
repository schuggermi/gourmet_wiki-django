from django.urls import path

from ingredients.views import ingredient_lookup_options, IngredientListView, ingredient_list_partial

app_name = 'ingredients'

urlpatterns = [
    # path('api/ingredient-lookup/', IngredientLookupSearchView.as_view(), name='ingredient-lookup-search'),
    path('ingredient-options/', ingredient_lookup_options, name='ingredient-options'),
    path("", IngredientListView.as_view(), name="ingredient_list"),
    path('partial/', ingredient_list_partial, name='ingredient_list_partial'),
]
