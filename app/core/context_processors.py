from django.conf import settings


def debug(request):
    """
    Add the DEBUG setting to the template context.
    """
    return {'debug': settings.DEBUG}


def seo_defaults(request):
    """Inject default SEO values into every template context."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Gourmet Wiki'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'https://gourmet-wiki.app'),
        'DEFAULT_DESCRIPTION': getattr(
            settings,
            'DEFAULT_DESCRIPTION',
            'Discover, cook, and master gourmet recipes.'
        ),
        'DEFAULT_KEYWORDS': getattr(
            settings,
            'DEFAULT_KEYWORDS',
            'gourmet recipes, recipe wiki, cooking techniques, ingredient guides'
        ),
        'DEFAULT_OG_IMAGE': getattr(
            settings,
            'DEFAULT_OG_IMAGE',
            settings.STATIC_URL + 'favicons/android-chrome-512x512.png'
        ),
        # Safe page-level defaults to prevent VariableDoesNotExist in templates
        'page_title': getattr(settings, 'SITE_NAME', 'Gourmet Wiki'),
        'page_description': getattr(
            settings,
            'DEFAULT_DESCRIPTION',
            'Discover, cook, and master gourmet recipes.'
        ),
        'page_keywords': getattr(
            settings,
            'DEFAULT_KEYWORDS',
            'gourmet recipes, recipe wiki, cooking techniques, ingredient guides'
        ),
        # Also provide OG/Twitter fallbacks so templates never fail resolution
        'og_title': getattr(settings, 'SITE_NAME', 'Gourmet Wiki'),
        'og_description': getattr(
            settings,
            'DEFAULT_DESCRIPTION',
            'Discover, cook, and master gourmet recipes.'
        ),
        'og_image': getattr(
            settings,
            'DEFAULT_OG_IMAGE',
            settings.STATIC_URL + 'favicons/android-chrome-512x512.png'
        ),
        'twitter_title': getattr(settings, 'SITE_NAME', 'Gourmet Wiki'),
        'twitter_description': getattr(
            settings,
            'DEFAULT_DESCRIPTION',
            'Discover, cook, and master gourmet recipes.'
        ),
        'twitter_image': getattr(
            settings,
            'DEFAULT_OG_IMAGE',
            settings.STATIC_URL + 'favicons/android-chrome-512x512.png'
        ),
    }