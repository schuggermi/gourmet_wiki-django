from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        return ['pages:home', 'pages:imprint', 'pages:privacy', 'pages:terms_of_use', 'wiki:wiki_index', 'recipes:recipe_list', 'ingredients:ingredient_list', 'menus:menu_list']

    def location(self, item):
        return reverse(item)
