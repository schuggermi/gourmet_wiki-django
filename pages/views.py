from django.db.models import Count, Avg, ExpressionWrapper, F, FloatField, Q
from django.shortcuts import render
from django.utils.timezone import now

from recipes.models import Recipe


def home(request):
    context = {}
    today = now().date()

    top_recipes = (
        Recipe.objects.annotate(
            avg_rating_today=Avg('ratings__score', filter=Q(ratings__rated_at__date=today))
        )
        .filter(avg_rating_today__isnull=False)
        .order_by('-avg_rating_today')[:4]
    )

    context['top_recipes'] = top_recipes

    return render(request, "pages/home.html", context)
