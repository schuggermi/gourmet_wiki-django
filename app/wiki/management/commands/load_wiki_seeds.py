import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pathlib import Path
import frontmatter
from django.utils.text import slugify

from wiki.models import WikiArticle, Category

User = get_user_model()


def copy_and_update_image_paths(markdown_content, source_dir: Path):
    def replacer(match):
        path = match.group(1).split('/')[-1]
        # Prüfe, ob es ein relativer Pfad ist (kein http(s))
        if not (path.startswith("http://") or path.startswith("https://")):
            source_path = source_dir / path
            print("Source path:", source_path)
            if source_path.exists():
                # Zielverzeichnis in MEDIA_ROOT/wiki_images/
                dest_dir = Path(settings.MEDIA_ROOT) / "wiki/images"
                print("Destination dir:", dest_dir)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / source_path.name

                print("DESTINATION PATH:", dest_path)
                shutil.copy2(source_path, dest_path)

                # Ersetze Pfad im Markdown durch MEDIA_URL
                return f"![]({settings.MEDIA_URL}wiki/images/{source_path.name})"
            else:
                # Datei nicht gefunden, lasse Pfad wie er ist
                return match.group(0)
        else:
            # Externe URL, nichts ändern
            return match.group(0)

    pattern = r"!\[\[([^\]]+\.(?:webp|png|jpeg|jpg))\]\]"
    matches = re.findall(pattern, markdown_content)
    if matches:
        print("Matches found:")
        for m in matches:
            print(m)
    else:
        print("No matches found.")

    # Then do your replacement
    updated_content = re.sub(pattern, replacer, markdown_content)

    return updated_content


class Command(BaseCommand):
    help = "Seed the database with Markdown wiki content"

    def handle(self, *args, **kwargs):
        path = Path('wiki/seed_articles/')
        files = list(path.glob("*.md"))
        if not files:
            self.stdout.write(self.style.WARNING("No Markdown files found in seed_articles/."))
            return

        for file in files:
            source_dir = Path(file.parent).joinpath('images')
            print("SOURCE DIR:", source_dir)
            post = frontmatter.load(file)

            title = post.get("title")
            slug = post.get("slug") or slugify(title)
            category_name = post.get("category", "")
            category = Category.objects.filter(name__iexact=category_name).first()

            if not category:
                category = Category.objects.create(name=category_name)

            is_draft = post.get("is_draft", False)
            version = post.get("version", 0.1)

            # Find or create the author
            author_email = post.get("author_email")
            author = None
            if author_email:
                try:
                    author, _ = User.objects.get(email=author_email)
                except User.DoesNotExist:
                    author = None

            updated_content = copy_and_update_image_paths(post.content, source_dir)
            post.content = updated_content

            # Create or update the article
            article, created = WikiArticle.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": category,
                    "content": post.content,
                    "author": author,
                    "is_draft": is_draft,
                    "version": version,
                }
            )

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {title}"))

        for article in WikiArticle.objects.all():
            article.save()
