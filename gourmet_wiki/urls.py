from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('pages.urls'), name='pages'),
                  path('recipes/', include('recipes.urls'), name='recipes'),
                  path('ingredients/', include('ingredients.urls'), name='ingredients'),
                  path('menus/', include('menus.urls'), name='menus'),
                  path('accounts/', include('allauth.urls')),
                  path('users/', include('users.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + debug_toolbar_urls()
