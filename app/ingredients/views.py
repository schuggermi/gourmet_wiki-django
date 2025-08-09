from django.shortcuts import render

from ingredients.models import IngredientLookup


def ingredient_lookup_options(request):
    q = request.GET.get('q', '')
    print(q)
    results = IngredientLookup.objects.filter(description__icontains=q).order_by('description')[:20] if q else []
    print(results)
    return render(request, 'ingredients/ingredient_options.html', {'ingredients': results})
