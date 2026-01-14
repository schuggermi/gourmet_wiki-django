from django.contrib.sitemaps import Sitemap
from .models import WikiArticle


class WikiSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return WikiArticle.objects.all()

    def lastmod(self, obj: WikiArticle):
        return obj.updated_at
