from . import settings


def cb_id(request):
    return {
        "CB_ID": settings.CB_ID
    }

def ga_id(request):
    return {
        "GA_ID": settings.GA_ID
    }
