from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('pages.urls'), name='pages'),
                  path('recipes/', include('recipes.urls'), name='recipes'),
                  path('ingredients/', include('ingredients.urls'), name='ingredients'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
