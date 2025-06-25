from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, DeleteView

from recipes.models import Recipe
from users.models import Profile

User = get_user_model()


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = '/'

    def get_object(self, queryset = ...):
        return User.objects.get(pk=self.request.user.pk)

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/profile.html"

    def get_object(self, queryset=...):
        user = User.objects.get(pk=self.request.user.pk)
        return user.profile if user else None


class UserRecipeListView(ListView):
    model = Recipe
    template_name = "users/recipe_list.html"

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).recipe_set.all()


class UserFavoriteRecipeListView(ListView):
    model = Recipe
    template_name = "users/favorite_recipe_list.html"

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).favorite_recipes.all()
