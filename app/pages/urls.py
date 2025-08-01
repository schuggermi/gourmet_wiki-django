from django.urls import path

from pages import views
from pages.views import imprint, privacy, terms_of_use

urlpatterns = [
    path('', views.home, name='home'),
    path('imprint/', imprint, name='imprint'),
    path('privacy/', privacy, name='privacy'),
    path('terms_of_use/', terms_of_use, name='terms_of_use'),
]
