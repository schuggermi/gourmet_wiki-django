from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from allauth.account.adapter import DefaultAccountAdapter
from allauth.core import context as allauth_context
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):

    def render_mail(self, template_prefix, email, context):
        """
        Render both text and HTML versions of email
        Returns: (subject, text_body, html_body)
        """
        request = context.get('request')

        # Subject
        subject = render_to_string(f'{template_prefix}_subject.txt', context, request=request)
        subject = ' '.join(subject.splitlines()).strip()

        # Text body
        text_body = render_to_string(f'{template_prefix}_message.txt', context, request=request)

        # HTML body (optional)
        html_body = None
        try:
            html_body = render_to_string(f'{template_prefix}_message.html', context, request=request)
        except Exception as e:
            logger.error(f"Error rendering HTML email template {template_prefix}_message.html: {e}")

        return subject, text_body, html_body

    def send_mail(self, template_prefix, email, context):
        """
        Send multipart email
        """
        # allauth's DefaultAccountAdapter.send_mail populates these
        request = getattr(allauth_context, 'request', None)
        ctx = {
            "request": request,
            "email": email,
            "current_site": get_current_site(request),
        }
        ctx.update(context)

        subject, text_body, html_body = self.render_mail(
            template_prefix, email, ctx
        )

        # Use text as the main body (required for EmailMultiAlternatives)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=self.get_from_email(),
            to=[email]
        )

        # Attach HTML as alternative if available
        if html_body:
            msg.attach_alternative(html_body, "text/html")

        msg.send()