from django.conf import settings


def debug(request):
    """
    Add the DEBUG setting to the template context.
    """
    return {'debug': settings.DEBUG}


def seo_defaults(request):
    """Globale SEO-Defaults für alle Templates"""
    return {
        'SITE_NAME': 'GourmetWiki',
        'SITE_TAGLINE': 'Deine #1 Wissensküche',
        'DEFAULT_DESCRIPTION': (
            'GourmetWiki - Keine Werbung. Kein Rätselraten. Einfach kochen. '
            'Rezepte von Köchen und leidenschaftlichen Hobbyköchen - '
            'gekocht, getestet und von der Community empfohlen.'
        ),
        'DEFAULT_KEYWORDS': (
            'Rezepte ohne Werbung, Koch-Community, Profi-Rezepte, GourmetWiki, '
            'Kochrezepte Deutsch, Rezepte von Köchen, kulinarische Community'
        ),
        'DEFAULT_OG_IMAGE': f"{request.scheme}://{request.get_host()}/static/images/og-default.jpg",
        'GA_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', 'G-BYM0XLT51B'),
        'CB_ID': getattr(settings, 'COOKIEBOT_ID', ''),
        'TWITTER_HANDLE': '@GourmetWiki',
    }