from django.contrib import admin
from reversion.admin import VersionAdmin

from wiki.models import WikiArticle


@admin.register(WikiArticle)
class WikiArticleAdmin(VersionAdmin):
    model = WikiArticle
    list_display = ('title', 'created_at', 'updated_at', 'is_draft', 'category', 'version')
