from django.db.models import F, Func, Value, CharField
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import TemplateView

from recipes.models import Recipe
from core.seo import SeoViewMixin, SeoData


# @login_required
def home(request):
    context = {}
    today = now().date()

    daily_random_recipes = (
        Recipe.objects.filter(is_published=True).annotate(
            hash_order=Func(
                Concat(
                    F('id'),
                    Value(str(today)),
                    output_field=CharField()  # 👈 This line is important
                ),
                function='md5',
                output_field=CharField()  # 👈 This is also required
            )
        )
        .order_by('hash_order')[:4]
    )

    context['daily_random_recipes'] = daily_random_recipes
    
    # SEO Data for Home
    seo_data = SeoData(
        title="GourmetWiki - Deine #1 Wissensküche | Keine Werbung. Kein Rätselraten. Einfach kochen.",
        description="Von Köchen und leidenschaftlichen Hobbyköchen. Rezepte, die gekocht, getestet und von der Community empfohlen werden.",
        keywords=["Rezepte", "Kochen", "Gourmet", "Wiki", "Wissensküche"],
        canonical_url=request.build_absolute_uri(request.path),
        og_type="website"
    )
    context['seo'] = seo_data

    return render(request, "pages/home.html", context)


class ImprintView(SeoViewMixin, TemplateView):
    template_name = 'pages/imprint.html'
    seo_title = "Impressum"
    seo_description = "Impressum von GourmetWiki"

class PrivacyView(SeoViewMixin, TemplateView):
    template_name = 'pages/privacy.html'
    seo_title = "Datenschutzerklärung"
    seo_description = "Datenschutzerklärung von GourmetWiki"

class TermsOfUseView(SeoViewMixin, TemplateView):
    template_name = 'pages/terms_of_use.html'
    seo_title = "Nutzungsbedingungen"
    seo_description = "Nutzungsbedingungen von GourmetWiki"

def imprint(request):
    return ImprintView.as_view()(request)


def privacy(request):
    return PrivacyView.as_view()(request)


def terms_of_use(request):
    return TermsOfUseView.as_view()(request)
