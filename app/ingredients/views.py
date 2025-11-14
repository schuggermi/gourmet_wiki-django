from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render
from django.utils import translation
from django.views.generic import ListView

from ingredients.models import IngredientLookup, Ingredient, Category


def ingredient_lookup_options(request):
    q = request.GET.get('q', '')
    print(q)

    if q:
        # Get the current language
        current_lang = translation.get_language()

        # First, try to find ingredients by their translated names
        translated_ingredients = Ingredient.objects.filter(
            translations__name__icontains=q,
            translations__language_code=current_lang
        ).distinct()

        # Then, find ingredients by their default names
        default_ingredients = Ingredient.objects.filter(name__icontains=q)

        # Combine the results, prioritizing translated matches
        results = list(translated_ingredients) + [i for i in default_ingredients if i not in translated_ingredients]
        results = results[:20]
    else:
        results = []

    print(results)
    return render(request, 'ingredients/ingredient_options.html', {'ingredients': results})


class IngredientListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "ingredients/ingredient_list.html"
    context_object_name = "ingredients"

    def get_queryset(self):
        queryset = super().get_queryset()
        print("QUERYSET: ", queryset)

        queryset = queryset.order_by("name")

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # print("QUERYSET: ", queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        context['search_query'] = search_query

        categories = Category.objects.order_by("name").all()
        object_list = []

        for category in categories:
            ingredients = self.get_queryset().filter(category=category)
            if ingredients.exists():
                object_list.append((category, ingredients))

        context["object_list"] = object_list
        return context


@login_required
def ingredient_list_partial(request):
    """
    View to render the ingredient list partial for htmx requests
    """
    search_query = request.GET.get('search', '')

    base_queryset = Ingredient.objects.all()

    if search_query:
        base_queryset = base_queryset.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    categories = Category.objects.order_by("name").all()
    object_list = []

    for category in categories:
        ingredients = base_queryset.filter(category=category).order_by("name")
        if ingredients.exists():
            object_list.append((category, ingredients))

    context = {
        'object_list': object_list,
        'search_query': search_query,
    }

    return render(request, 'ingredients/partials/ingredient_list.html', context)
