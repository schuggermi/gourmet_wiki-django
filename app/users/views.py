from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, DeleteView
from django.http import JsonResponse

from recipes.models import Recipe
from users.models import Profile

User = get_user_model()


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    # Render a modal partial like recipe delete instead of a full page
    template_name = 'users/partials/delete_confirmation_modal.html'
    success_url = '/'

    def get_object(self, queryset = ...):
        return User.objects.get(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        # Serve the delete confirmation modal HTML (to be fetched dynamically)
        user = self.get_object()
        return render(request, self.template_name, {"user_obj": user})

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        # Validate confirmation inputs (keep name/email confirmation logic)
        confirm_name = request.POST.get('confirm_name', '').strip()
        confirm_email = request.POST.get('confirm_email', '').strip()

        expected_name = user.get_full_name().strip()
        expected_email = user.email.strip()

        if confirm_name != expected_name or confirm_email != expected_email:
            # Re-render modal with inline field errors; keep modal open
            errors = {}
            if confirm_name != expected_name:
                errors['confirm_name'] = _('The entered name does not match your full name.')
            if confirm_email != expected_email:
                errors['confirm_email'] = _('The entered email does not match your email address.')

            context = {
                "user_obj": user,
                "form_errors": errors,
                "values": {
                    "confirm_name": confirm_name,
                    "confirm_email": confirm_email,
                },
            }
            # Return 400 so client script knows to update modal content
            return render(request, self.template_name, context=context, status=400)

        # Proceed with deletion
        # If the request is AJAX (modal submit), delete and return JSON redirect
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Delete user and respond with redirect URL
            user.delete()
            return JsonResponse({"redirect_url": "/"})

        response = super().post(request, *args, **kwargs)
        messages.success(request, _('Your account has been deleted.'))
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/profile.html"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")

        if username:
            user: User = get_object_or_404(User, username=username)
        else:
            user: User = self.request.user

        return user.profile


class UserRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "users/recipe_list.html"

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).recipe_set.all()


class UserFavoriteRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "users/favorite_recipe_list.html"

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).favorite_recipes.all()
