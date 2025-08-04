import re

from django.utils import translation


class ForceGermanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('de')
        request.LANGUAGE_CODE = 'de'
        response = self.get_response(request)
        translation.deactivate()
        return response


from django.shortcuts import redirect
from django.conf import settings

EXEMPT_URLS = [
    '/accounts/login/',
    '/accounts/logout/',
    re.compile(r'^accounts/confirm-email/?$'),
    re.compile(r'^accounts/confirm-email/.+/?$'),  # <-- key part!
    '/admin/',
    '/imprint/',
    '/privacy/',
    '/terms_of_use/',
]


class RequireLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if path in EXEMPT_URLS or path.startswith('/static/'):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
