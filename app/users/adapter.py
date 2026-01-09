from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def render_mail(self, template_prefix, email, context):
        """
        Render both text and HTML versions of email
        Returns: (subject, text_body, html_body)
        """
        # Subject
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = ' '.join(subject.splitlines()).strip()

        # Text body
        text_body = render_to_string(f'{template_prefix}_message.txt', context)

        # HTML body (optional)
        html_body = None
        try:
            html_body = render_to_string(f'{template_prefix}_message.html', context)
        except Exception:
            pass

        return subject, text_body, html_body

    def send_mail(self, template_prefix, email, context):
        """
        Send multipart email
        """
        subject, text_body, html_body = self.render_mail(
            template_prefix, email, context
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=self.get_from_email(),
            to=[email]
        )

        if html_body:
            msg.attach_alternative(html_body, "text/html")

        msg.send()
