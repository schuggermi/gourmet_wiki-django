from django.contrib.sitemaps import Sitemap
from .models import Menu


class MenuSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Menu.objects.all()

    def lastmod(self, obj: Menu):
        return obj.updated_at
