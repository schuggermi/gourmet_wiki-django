from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.models import Site
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from gourmet_wiki import settings

User = get_user_model()


@login_required
def signup_disabled(request):
    return HttpResponseForbidden()


def is_debug_mode(user):
    return settings.DEBUG


from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist


@user_passes_test(is_debug_mode)
def preview_email(request, template_name=None):
    """Preview email templates (both .txt and .html versions)"""

    user = request.user if request.user.is_authenticated else User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )

    current_site = Site.objects.get_current()

    # Template prefix mapping (without extensions)
    template_prefixes = {
        'email_confirmation': 'account/email/email_confirmation_message',
        'password_reset': 'account/email/password_reset_key_message',
        'email_changed': 'account/email/email_changed_message',
        'password_changed': 'account/email/password_changed_message',
    }

    template_prefix = template_prefixes.get(template_name)

    if not template_prefix:
        return render(request, 'debug/email_preview_list.html', {
            'available_templates': template_prefixes.keys()
        })

    # Context for rendering
    context = {
        'user': user,
        'current_site': current_site,
        'activate_url': f"http://{current_site.domain}/accounts/confirm-email/ABC123/",
        'password_reset_url': f"http://{current_site.domain}/accounts/password/reset/key/XYZ789/",
        'key': 'SAMPLE-KEY-123',
        'uid': 'MQ',
    }

    # Try to render both text and HTML versions
    text_content = None
    html_content = None
    subject = None

    # Debug info
    errors = {}

    # Subject
    subject_template = template_prefix.replace('_message', '_subject') + '.txt'
    try:
        subject = render_to_string(subject_template, context, request=request)
        subject = ' '.join(subject.splitlines()).strip()
    except Exception as e:
        subject = "Subject template error"
        errors['subject'] = f"{type(e).__name__}: {str(e)}"

    # Plain text version
    try:
        text_content = render_to_string(f'{template_prefix}.txt', context, request=request)
    except Exception as e:
        errors['text'] = f"{type(e).__name__}: {str(e)}"

    # HTML version - CATCH ALL EXCEPTIONS TO SEE REAL ERROR
    try:
        html_content = render_to_string(f'{template_prefix}.html', context, request=request)
    except Exception as e:
        # This will show the REAL error
        import traceback
        errors['html'] = f"{type(e).__name__}: {str(e)}"
        errors['html_traceback'] = traceback.format_exc()

    # Additional debug: Check if template files exist
    template_checks = {}
    for ext in ['txt', 'html']:
        template_path = f'{template_prefix}.{ext}'
        try:
            get_template(template_path)
            template_checks[ext] = '✓ Found'
        except Exception as e:
            template_checks[ext] = f'✗ {type(e).__name__}'

    return render(request, 'debug/email_preview.html', {
        'subject': subject,
        'html_content': html_content,
        'text_content': text_content,
        'template_name': template_name,
        'template_prefix': template_prefix,
        'context': context,
        'has_html': html_content is not None,
        'has_text': text_content is not None,
        'errors': errors,
        'template_checks': template_checks,
    })


@user_passes_test(is_debug_mode)
def preview_email_content(request, template_name):
    """Return just the HTML content for iframe"""

    user = request.user if request.user.is_authenticated else User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )

    current_site = Site.objects.get_current()

    template_prefixes = {
        'email_confirmation': 'account/email/email_confirmation_message',
        'password_reset': 'account/email/password_reset_key_message',
        'email_changed': 'account/email/email_changed_message',
        'password_changed': 'account/email/password_changed_message',
    }

    template_prefix = template_prefixes.get(template_name)

    if not template_prefix:
        return HttpResponse("Template not found", status=404)

    context = {
        'user': user,
        'current_site': current_site,
        'activate_url': f"http://{current_site.domain}/accounts/confirm-email/ABC123/",
        'password_reset_url': f"http://{current_site.domain}/accounts/password/reset/key/XYZ789/",
        'key': 'SAMPLE-KEY-123',
        'uid': 'MQ',
    }

    try:
        html_content = render_to_string(f'{template_prefix}.html', context, request=request)
        return HttpResponse(html_content, content_type='text/html')
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
