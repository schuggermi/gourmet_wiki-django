from django.urls import path

from users.views import ProfileView, UserRecipeListView

urlpatterns = [
    path('me/profile/', ProfileView.as_view(), name='users-profile'),
    path('me/recipes/', UserRecipeListView.as_view(), name='users-profile-recipes'),
]