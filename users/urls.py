from django.urls import path

from users.views import ProfileView, UserRecipeListView, UserFavoriteRecipeListView

urlpatterns = [
    path('me/profile/', ProfileView.as_view(), name='users-profile'),
    path('me/recipes/', UserRecipeListView.as_view(), name='users-profile-recipes'),
    path('me/recipes/favorites/', UserFavoriteRecipeListView.as_view(), name='users-profile-favorite-recipes'),
]
