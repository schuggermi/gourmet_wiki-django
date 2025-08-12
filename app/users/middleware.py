from django.conf import settings
from django.shortcuts import resolve_url
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class HTMXLoginRedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if (
                request.headers.get("HX-Request") == "true"
                and response.status_code == 302
                and resolve_url(settings.LOGIN_URL) in response["Location"]
        ):
            return JsonResponse({
                "redirect": response["Location"],
            }, status=401)
        return response
