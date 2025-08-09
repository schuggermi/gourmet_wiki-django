from django.urls import path

from wiki.views import test, WikiArticleListView, WikiArticleDetailView

app_name = "wiki"

urlpatterns = [
    path('test/', test, name='test'),
    path("", WikiArticleListView.as_view(), name="article_list"),
    path("<slug:slug>/", WikiArticleDetailView.as_view(), name="article_detail"),
]
