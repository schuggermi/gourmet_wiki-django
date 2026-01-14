import logging
import re

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from core.seo import SeoData

User = get_user_model()

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WikiArticle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_draft = models.BooleanField(default=False)
    rendered_html = models.TextField(editable=False, blank=True)

    def save(self, *args, **kwargs):
        import markdown

        if not self.slug:
            self.slug = slugify(self.title)

        # Step 1: Convert Markdown to HTML
        html = markdown.markdown(
            "\n\n\n".join(
                line if line.strip() else "<br>"
                for line in self.content.splitlines()
            ),
            extensions=["extra", "codehilite", "toc", "nl2br"],
        )

        # Step 2: Replace [[wikilinks]] with anchor tags
        def replace_wikilink(match):
            title = match.group(1).strip()
            linked_article = WikiArticle.objects.filter(title__iexact=title)

            if linked_article.exists():
                linked_article = linked_article[0]
                url = f"/wiki/{linked_article.slug}/"
                return f'<a href="{url}" class="link">{title}</a>'
            else:
                return f'<a href="" class="missing-link">{title}</a>'

        html = re.sub(
            r"(?<!\!)\[\[([^\[\]]+)\]\](?!\(\))",
            replace_wikilink,
            html
        )

        # Save the final rendered HTML
        self.rendered_html = html
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('wiki:article_detail', kwargs={'slug': self.slug})

    def get_seo_data(self, request) -> SeoData:
        keywords = [self.title, "Wiki", "GourmetWiki"]
        if self.category:
            keywords.append(self.category.name)

        json_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self.title,
            "description": self.summary,
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username if self.author else "GourmetWiki"
            },
            "datePublished": self.created_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
        }

        return SeoData(
            title=f"{self.title} - Wiki",
            description=self.summary[:160] if self.summary else f"Lies den Artikel {self.title} auf GourmetWiki.",
            keywords=keywords,
            canonical_url=request.build_absolute_uri(self.get_absolute_url()),
            og_type="article",
            json_ld=json_ld
        )
