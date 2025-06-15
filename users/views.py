from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from recipes.models import Recipe
from users.models import Profile

User = get_user_model()


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/profile.html"

    def get_object(self, queryset=...):
        return User.objects.get(pk=self.request.user.pk).profile


class UserRecipeListView(ListView):
    model = Recipe
    template_name = "users/recipe_list.html"

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).recipe_set.all()
