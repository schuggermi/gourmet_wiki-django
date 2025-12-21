from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('secure/admin/', admin.site.urls),
]
