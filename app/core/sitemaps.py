from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        # Adjust to match your actual static views
        return ['home', 'imprint', 'privacy', 'terms_of_use']

    def location(self, item):
        return reverse(item)
