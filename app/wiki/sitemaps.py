from django.contrib.sitemaps import Sitemap
from .models import WikiPage


class WikiSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return WikiPage.objects.all()

    def lastmod(self, obj: WikiPage):
        return obj.updated_at
