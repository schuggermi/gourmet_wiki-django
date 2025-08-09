from django.shortcuts import render
from django.views.generic import ListView, DetailView

from wiki.models import WikiArticle, Category


def test(request):
    context = {
        'articles': WikiArticle.objects.all(),
    }
    return render(request, 'wiki/test.html', context=context)


class WikiArticleListView(ListView):
    model = WikiArticle
    template_name = "wiki/article_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return WikiArticle.objects.filter(is_draft=False).order_by("title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.order_by("name").all()

        category_articles = []
        for category in categories:
            articles = WikiArticle.objects.filter(
                is_draft=False,
                category=category
            ).order_by("title")
            if articles.exists():
                category_articles.append((category, articles))

        context["category_articles"] = category_articles
        return context


class WikiArticleDetailView(DetailView):
    model = WikiArticle
    template_name = "wiki/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"
