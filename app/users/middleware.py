from django.conf import settings
from django.contrib import messages
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
            messages.info(request, "🚧 Access Limited | We’re cooking something up!")

            # get the last message text
            message = list(messages.get_messages(request))[-1].message

            return JsonResponse({
                "redirect": response["Location"],
                "message": message,
                "message_tags": "info"
            }, status=401)
        return response
