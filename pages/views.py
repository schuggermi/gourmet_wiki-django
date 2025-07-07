from django.db.models import Count, Avg, ExpressionWrapper, F, FloatField, Q, Func, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils.timezone import now

from recipes.models import Recipe


def home(request):
    context = {}
    today = now().date()

    daily_random_recipes = (
        Recipe.objects.filter(is_published=True).annotate(
            hash_order=Func(
                Concat(
                    F('id'),
                    Value(str(today)),
                    output_field=CharField()  # 👈 This line is important
                ),
                function='md5',
                output_field=CharField()  # 👈 This is also required
            )
        )
        .order_by('hash_order')[:4]
    )

    context['daily_random_recipes'] = daily_random_recipes

    return render(request, "pages/home.html", context)
