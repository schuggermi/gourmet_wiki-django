from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap
from recipes.sitemaps import RecipeSitemap
from wiki.sitemaps import WikiSitemap
from ingredients.sitemaps import IngredientSitemap
from menus.sitemaps import MenuSitemap


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)


urlpatterns = [
                  path('test/404/', lambda request: render(request, "errors/404.html", status=404)),
                  path('test/500/', lambda request: render(request, "errors/500.html", status=404)),
                  path('test/403/', lambda request: render(request, "errors/403.html", status=404)),
                  # i18n: enable Django's built-in language switch endpoint at /i18n/setlang/
                  path('i18n/', include('django.conf.urls.i18n')),
                  path('', include('pages.urls'), name='pages'),
                  path('', include('core.urls'), name='core'),
                  path('wiki/', include('wiki.urls'), name='wiki'),
                  path('recipes/', include('recipes.urls'), name='recipes'),
                  path('ingredients/', include('ingredients.urls'), name='ingredients'),
                  path('menus/', include('menus.urls'), name='menus'),
                  path('accounts/', include('allauth.urls')),
                  path('', include('users.urls')),
                  path('api-auth/', include('rest_framework.urls')),
                  path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
                  path('sitemap.xml', sitemap, {'sitemaps': {
                      'static': StaticViewSitemap,
                      'recipes': RecipeSitemap,
                      'wiki': WikiSitemap,
                      'ingredients': IngredientSitemap,
                      'menus': MenuSitemap,
                  }}, name='sitemap'),
                  path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots_txt'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
