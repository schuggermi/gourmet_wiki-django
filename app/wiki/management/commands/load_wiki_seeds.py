from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pathlib import Path
import frontmatter
from django.utils.text import slugify

from wiki.models import WikiArticle

User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with Markdown wiki content"

    def handle(self, *args, **kwargs):
        path = Path('wiki/seed_articles/')
        files = list(path.glob("*.md"))
        if not files:
            self.stdout.write(self.style.WARNING("No Markdown files found in seed_articles/."))
            return

        for file in files:
            post = frontmatter.load(file)

            title = post.get("title")
            slug = post.get("slug") or slugify(title)
            summary = post.get("summary", "")
            category = post.get("category", "")
            is_draft = post.get("is_draft", False)

            # Find or create the author
            author_email = post.get("author_email")
            author = None
            if author_email:
                try:
                    author, _ = User.objects.get(email=author_email)
                except User.DoesNotExist:
                    author = None

            # Create or update the article
            article, created = WikiArticle.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "category": category,
                    "content": post.content,
                    "author": author,
                    "is_draft": is_draft,
                }
            )

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {title}"))
