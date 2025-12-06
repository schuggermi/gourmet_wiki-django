from . import settings


def cb_id(request):
    print("Context processor sending:", settings.CB_ID)
    return {
        "CB_ID": settings.CB_ID
    }

def ga_id(request):
    return {
        "GA_ID": settings.GA_ID
    }
