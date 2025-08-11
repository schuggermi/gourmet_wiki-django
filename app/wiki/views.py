from django.db.models import Q
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
        queryset = super().get_queryset()
        queryset = queryset.filter(is_draft=False).order_by("title")

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        context['search_query'] = search_query

        categories = Category.objects.order_by("name").all()
        object_list = []

        for category in categories:
            articles = self.get_queryset().filter(category=category)
            if articles.exists():
                object_list.append((category, articles))

        context["object_list"] = object_list
        return context


def article_list_partial(request):
    """
    View to render the article list partial for htmx requests
    """
    search_query = request.GET.get('search', '')

    base_queryset = WikiArticle.objects.filter(is_draft=False)

    if search_query:
        base_queryset = base_queryset.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    categories = Category.objects.order_by("name").all()
    object_list = []

    for category in categories:
        articles = base_queryset.filter(category=category).order_by("title")
        if articles.exists():
            object_list.append((category, articles))

    context = {
        'object_list': object_list,
        'search_query': search_query,
    }

    return render(request, 'wiki/partials/article_list.html', context)


class WikiArticleDetailView(DetailView):
    model = WikiArticle
    template_name = "wiki/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"
