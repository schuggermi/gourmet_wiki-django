# # views.py - Beispiele für die Context-Daten in deinen Views
#
# from django.views.generic import DetailView, ListView
# from django.contrib.seo.models import Recipe, Category
#
#
# # ==========================================
# # REZEPT DETAIL VIEW
# # ==========================================
# class RecipeDetailView(DetailView):
#     model = Recipe
#     template_name = 'recipes/recipe_detail.html'
#     context_object_name = 'recipe'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         recipe = self.get_object()
#
#         # SEO Meta Tags
#         context['page_title'] = recipe.title
#         context['page_description'] = (
#             recipe.description[:160] if recipe.description
#             else f"Entdecke das Rezept für {recipe.title} auf GourmetWiki. "
#                  f"Von Profis entwickelt, Schritt für Schritt erklärt."
#         )
#         context['page_keywords'] = self._generate_recipe_keywords(recipe)
#
#         # Open Graph / Social Media
#         context['og_title'] = f"{recipe.title} - Rezept auf GourmetWiki"
#         context['og_description'] = recipe.description[:200] if recipe.description else context['page_description']
#         context['og_image'] = recipe.image.url if recipe.image else None
#         context['og_type'] = 'article'
#
#         # Twitter Card
#         context['twitter_title'] = f"{recipe.title} - Rezept"
#         context['twitter_description'] = recipe.description[:160] if recipe.description else context['page_description']
#         context['twitter_image'] = recipe.image.url if recipe.image else None
#         context['twitter_creator'] = f"@{recipe.author.twitter_handle}" if hasattr(recipe.author,
#                                                                                    'twitter_handle') else "@GourmetWiki"
#
#         # Canonical URL
#         context['canonical_url'] = self.request.build_absolute_uri(recipe.get_absolute_url())
#
#         # Zusätzliche Daten für Schema.org (bereits im Template, aber hier zur Info)
#         context['recipe'] = recipe  # Enthält: ingredients, steps, ratings, etc.
#
#         return context
#
#     def _generate_recipe_keywords(self, recipe):
#         """Generiert relevante Keywords für das Rezept"""
#         keywords = [recipe.title, f"Rezept {recipe.title}"]
#
#         if recipe.category:
#             keywords.append(recipe.category.name)
#
#         # Tags hinzufügen
#         keywords.extend([tag.name for tag in recipe.tags.all()[:5]])
#
#         # Cuisine hinzufügen wenn vorhanden
#         if hasattr(recipe, 'cuisine') and recipe.cuisine:
#             keywords.append(recipe.cuisine)
#
#         # Ernährungsformen
#         if recipe.is_vegetarian:
#             keywords.append('vegetarisch')
#         if recipe.is_vegan:
#             keywords.append('vegan')
#         if recipe.is_gluten_free:
#             keywords.append('glutenfrei')
#
#         keywords.append('GourmetWiki Rezept')
#
#         return ', '.join(keywords)
#
#
# # ==========================================
# # KATEGORIE LIST VIEW
# # ==========================================
# class CategoryDetailView(ListView):
#     model = Recipe
#     template_name = 'recipes/category_detail.html'
#     context_object_name = 'recipes'
#     paginate_by = 24
#
#     def get_queryset(self):
#         self.category = Category.objects.get(slug=self.kwargs['slug'])
#         return Recipe.objects.filter(
#             category=self.category,
#             is_published=True
#         ).select_related('author', 'category').prefetch_related('tags')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         category = self.category
#
#         # Anzahl der Rezepte in dieser Kategorie
#         recipe_count = self.get_queryset().count()
#
#         # SEO Meta Tags
#         context['page_title'] = f"{category.name} Rezepte"
#         context['page_description'] = self._generate_category_description(category, recipe_count)
#         context['page_keywords'] = self._generate_category_keywords(category)
#
#         # Open Graph
#         context['og_title'] = f"{category.name} Rezepte - GourmetWiki"
#         context['og_description'] = (
#             category.description[:200] if category.description
#             else f"Entdecke {recipe_count} {category.name} Rezepte auf GourmetWiki."
#         )
#         context['og_image'] = category.image.url if category.image else None
#
#         # Twitter Card
#         context['twitter_title'] = f"{category.name} Rezepte"
#         context['twitter_description'] = context['page_description']
#         context['twitter_image'] = category.image.url if category.image else None
#
#         # Canonical URL
#         context['canonical_url'] = self.request.build_absolute_uri(category.get_absolute_url())
#
#         # Zusätzliche Context-Daten
#         context['category'] = category
#         context['category'].recipe_count = recipe_count
#         context['category'].subcategories = category.children.all() if hasattr(category, 'children') else []
#
#         return context
#
#     def _generate_category_description(self, category, recipe_count):
#         """Generiert SEO-optimierte Beschreibung für die Kategorie"""
#         if category.description:
#             # Nehme die ersten 150 Zeichen der Beschreibung
#             base_desc = category.description[:150]
#             if len(category.description) > 150:
#                 base_desc = base_desc.rsplit(' ', 1)[0] + '...'
#             return base_desc
#
#         # Fallback: Generierte Beschreibung
#         return (
#             f"Entdecke {recipe_count} {category.name} Rezepte auf GourmetWiki. "
#             f"Von Profis entwickelt, von der Community getestet. "
#             f"Keine Werbung, nur authentische Rezepte."
#         )
#
#     def _generate_category_keywords(self, category):
#         """Generiert Keywords für die Kategorie"""
#         keywords = [
#             category.name,
#             f"{category.name} Rezepte",
#             f"GourmetWiki {category.name}",
#         ]
#
#         # Unterkategorien als Keywords
#         if hasattr(category, 'children'):
#             subcategories = category.children.all()[:5]
#             keywords.extend([sub.name for sub in subcategories])
#
#         # Parent Category
#         if category.parent_category:
#             keywords.append(category.parent_category.name)
#
#         keywords.append('Koch-Rezepte')
#         keywords.append('kochen ohne Werbung')
#
#         return ', '.join(keywords)
#
#
# # ==========================================
# # STARTSEITE / HOME VIEW
# # ==========================================
# class HomeView(ListView):
#     model = Recipe
#     template_name = 'home.html'
#     context_object_name = 'featured_recipes'
#
#     def get_queryset(self):
#         # Featured/Beliebte Rezepte
#         return Recipe.objects.filter(
#             is_published=True,
#             is_featured=True
#         ).select_related('author', 'category')[:12]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Startseite braucht keine speziellen Meta-Tags, da sie im base.html definiert sind
#         # Aber wir können sie überschreiben falls gewünscht:
#         context['page_title'] = 'GourmetWiki'
#         context['page_description'] = (
#             'Deine #1 Wissensküche - Keine Werbung. Kein Rätselraten. Einfach kochen. '
#             'Von Köchen und leidenschaftlichen Hobbyköchen. Rezepte, die gekocht, '
#             'getestet und von der Community empfohlen werden.'
#         )
#
#         # Zusätzliche Daten für die Startseite
#         context['popular_categories'] = Category.objects.annotate(
#             recipe_count=Count('recipes')
#         ).filter(recipe_count__gt=0).order_by('-recipe_count')[:8]
#
#         context['recent_recipes'] = Recipe.objects.filter(
#             is_published=True
#         ).order_by('-created_at')[:8]
#
#         context['top_rated_recipes'] = Recipe.objects.filter(
#             is_published=True,
#             average_rating__gte=4.5
#         ).order_by('-average_rating', '-review_count')[:8]
#
#         return context
#
#
# # ==========================================
# # CONTEXT PROCESSOR (settings.py)
# # ==========================================
# # Füge dies zu TEMPLATES['OPTIONS']['context_processors'] hinzu:
# # 'your_app.context_processors.seo_defaults'
#
# # context_processors.py
# from django.conf import settings
#
#
# def seo_defaults(request):
#     """Globale SEO-Defaults für alle Templates"""
#     return {
#         'SITE_NAME': 'GourmetWiki',
#         'SITE_TAGLINE': 'Deine #1 Wissensküche',
#         'DEFAULT_DESCRIPTION': (
#             'GourmetWiki - Keine Werbung. Kein Rätselraten. Einfach kochen. '
#             'Rezepte von Köchen und leidenschaftlichen Hobbyköchen - '
#             'gekocht, getestet und von der Community empfohlen.'
#         ),
#         'DEFAULT_KEYWORDS': (
#             'Rezepte ohne Werbung, Koch-Community, Profi-Rezepte, GourmetWiki, '
#             'Kochrezepte Deutsch, Rezepte von Köchen, kulinarische Community'
#         ),
#         'DEFAULT_OG_IMAGE': f"{request.scheme}://{request.get_host()}/static/images/og-default.jpg",
#         'GA_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', 'G-BYM0XLT51B'),
#         'CB_ID': getattr(settings, 'COOKIEBOT_ID', ''),
#         'TWITTER_HANDLE': '@GourmetWiki',
#     }
#
#
# # ==========================================
# # MODELS - Hilfreiche Methoden
# # ==========================================
# # models.py
#
# class Recipe(models.Model):
#     # ... deine Felder ...
#
#     def get_absolute_url(self):
#         """Gibt die kanonische URL des Rezepts zurück"""
#         from django.urls import reverse
#         return reverse('recipe_detail', kwargs={'slug': self.slug})
#
#     @property
#     def total_time(self):
#         """Gesamtzeit für Schema.org"""
#         return (self.prep_time or 0) + (self.cook_time or 0)
#
#     @property
#     def average_rating(self):
#         """Durchschnittliche Bewertung"""
#         ratings = self.ratings.all()
#         if not ratings:
#             return 0
#         return sum(r.rating for r in ratings) / len(ratings)
#
#     @property
#     def review_count(self):
#         """Anzahl der Bewertungen"""
#         return self.ratings.count()
#
#
# class Category(models.Model):
#     # ... deine Felder ...
#
#     def get_absolute_url(self):
#         """Gibt die kanonische URL der Kategorie zurück"""
#         from django.urls import reverse
#         return reverse('category_detail', kwargs={'slug': self.slug})
#
#     @property
#     def recipe_count(self):
#         """Anzahl der Rezepte in dieser Kategorie"""
#         return self.recipes.filter(is_published=True).count()