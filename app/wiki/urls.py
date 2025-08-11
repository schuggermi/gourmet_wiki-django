from django.urls import path

from wiki.views import test, WikiArticleListView, WikiArticleDetailView, article_list_partial

app_name = "wiki"

urlpatterns = [
    path('test/', test, name='test'),
    path("", WikiArticleListView.as_view(), name="article_list"),
    path('partial/', article_list_partial, name='article_list_partial'),
    path("<slug:slug>/", WikiArticleDetailView.as_view(), name="article_detail"),
]
