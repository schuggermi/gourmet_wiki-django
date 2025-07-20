from django.conf import settings

def debug(request):
    """
    Add the DEBUG setting to the template context.
    """
    return {'debug': settings.DEBUG}