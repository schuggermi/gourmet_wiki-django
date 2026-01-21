from . import settings


def cb_id(request):
    return {
        "VITE_CB_ID": settings.VITE_CB_ID
    }

def ga_id(request):
    return {
        "VITE_GA_ID": settings.VITE_GA_ID
    }
