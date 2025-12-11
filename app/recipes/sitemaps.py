from django.contrib.sitemaps import Sitemap
from .models import Recipe


class RecipeSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Recipe.objects.filter(is_published=True)

    def lastmod(self, obj: Recipe):
        # We only have created_at on the model; use it as lastmod
        return obj.created_at
