from django.urls import path

from wiki.views import test

urlpatterns = [
    path('test/', test, name='test'),
]