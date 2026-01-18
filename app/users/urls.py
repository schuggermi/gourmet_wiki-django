from django.urls import path

from users.views import ProfileView, UserRecipeListView, UserFavoriteRecipeListView, UserDeleteView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('me/settings/account/delete/', UserDeleteView.as_view(), name='profile_delete'),
    path('cookbook/', UserRecipeListView.as_view(), name='cookbook'),
    path('favorites/', UserFavoriteRecipeListView.as_view(), name='favorites'),
]
