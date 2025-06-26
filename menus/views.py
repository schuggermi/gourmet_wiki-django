from django.views.generic import ListView, DetailView

from menus.models import Menu
from recipes.utils import calculate_scaled_ingredients_menu


class MenuListView(ListView):
    model = Menu


class MenuDetailView(DetailView):
    model = Menu

    def get_context_data(self, **kwargs):
        context = super(MenuDetailView, self).get_context_data(**kwargs)
        context.update(calculate_scaled_ingredients_menu(self.object.pk, self.object.portions))
        return context
