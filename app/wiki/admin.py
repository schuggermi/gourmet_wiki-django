from django.contrib import admin
from reversion.admin import VersionAdmin

from wiki.models import WikiArticle, Category


@admin.register(WikiArticle)
class WikiArticleAdmin(VersionAdmin):
    model = WikiArticle
    list_display = ('title', 'created_at', 'updated_at', 'is_draft', 'category', 'version')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ('name', 'slug')
