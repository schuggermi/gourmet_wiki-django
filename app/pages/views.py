from django.contrib.auth.decorators import login_required
from django.db.models import F, Func, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils.timezone import now

from recipes.models import Recipe


# @login_required
def home(request):
    context = {}
    today = now().date()

    daily_random_recipes = (
        Recipe.objects.annotate( # .filter(is_published=True)
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


def imprint(request):
    return render(request, 'pages/imprint.html')


def privacy(request):
    return render(request, 'pages/privacy.html')


def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')
