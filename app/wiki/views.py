from django.shortcuts import render

from wiki.models import WikiArticle


def test(request):
    context = {
        'articles': WikiArticle.objects.all(),
    }
    return render(request, 'wiki/test.html', context=context)
