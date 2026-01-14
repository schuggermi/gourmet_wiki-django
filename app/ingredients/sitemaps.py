from django.contrib.sitemaps import Sitemap
from .models import Ingredient


class IngredientSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Ingredient.objects.all()
