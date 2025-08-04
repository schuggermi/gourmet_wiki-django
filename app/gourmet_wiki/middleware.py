import logging
import re

from django.http import HttpResponse
from django.utils import translation
from django_ratelimit.core import get_usage


class ForceGermanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('de')
        request.LANGUAGE_CODE = 'de'
        response = self.get_response(request)
        translation.deactivate()
        return response


class GlobalRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_client_ip(request):
        """Return the real IP address of the client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __call__(self, request):
        ip = self.get_client_ip(request)

        usage = get_usage(
            group='global',
            key=lambda r, req: ip,
            rate='5/m',
            request=request,
            increment=True
        )

        if usage['should_limit']:
            return HttpResponse("Rate limit exceeded", status=429)

        return self.get_response(request)


class SuspiciousRequestMiddleware:
    SUSPICIOUS_PATHS = {
        "/index.php",
        "/wp-admin/setup-config.php",
        "/public/index.php",
        "/wordpress/wp-admin/setup-config.php",
        "/containers/json",
        "/favicon.ico",
    }

    SUSPICIOUS_PATTERNS = [
        "phpunit",
        "eval-stdin.php",
        "wp-admin",
        "setup-config.php",
        "index.php",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        ip = request.META.get('REMOTE_ADDR', 'unknown')

        if path in self.SUSPICIOUS_PATHS:
            logging.warning(f"Suspicious exact request from IP {ip} to {request.path}")
        elif any(pattern in path for pattern in self.SUSPICIOUS_PATTERNS):
            logging.warning(f"Suspicious pattern request from IP {ip} to {request.path}")

        return self.get_response(request)


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
