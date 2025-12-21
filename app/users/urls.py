from django.urls import path

from users.views import ProfileView, UserRecipeListView, UserFavoriteRecipeListView, UserDeleteView

urlpatterns = [
    path('profile/<str:username>/', ProfileView.as_view(), name='user-profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('me/settings/account/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('me/cookbook/', UserRecipeListView.as_view(), name='users-profile-recipes'),
    path('me/favorites/', UserFavoriteRecipeListView.as_view(), name='users-profile-favorite-recipes'),
]
