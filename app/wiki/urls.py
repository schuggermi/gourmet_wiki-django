from django.urls import path

import wiki.views as views

app_name = "wiki"

urlpatterns = [
    path("", views.WikiArticleListView.as_view(), name="article_list"),
    path('partial/', views.article_list_partial, name='article_list_partial'),
    path("<slug:slug>/", views.WikiArticleDetailView.as_view(), name="article_detail"),
]
