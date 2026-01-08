from django.contrib import admin
from django.urls import path

from gourmet_wiki import settings

urlpatterns = [
    path('secure/admin/', admin.site.urls),
]

if settings.DEBUG:
    from .views import preview_email, preview_email_content

    urlpatterns += [
        path('debug/emails/', preview_email, name='email-preview-list'),
        path('debug/emails/<str:template_name>/', preview_email, name='email-preview'),
        path('debug/emails/<str:template_name>/content/', preview_email_content, name='email-preview-content'),
    ]

