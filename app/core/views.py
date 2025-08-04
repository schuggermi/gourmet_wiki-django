from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


@login_required
def signup_disabled(request):
    return HttpResponseForbidden()
