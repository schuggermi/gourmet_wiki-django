from django.urls import path

from users.views import ProfileView, UserRecipeListView, UserFavoriteRecipeListView, UserDeleteView

urlpatterns = [
    path('me/profile/', ProfileView.as_view(), name='users-profile'),
    path('me/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('me/cookbook/', UserRecipeListView.as_view(), name='users-profile-recipes'),
    path('me/favorites/', UserFavoriteRecipeListView.as_view(), name='users-profile-favorite-recipes'),
]
