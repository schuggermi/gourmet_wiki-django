from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class WikiArticle(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    version = models.PositiveIntegerField(default=1)
    is_draft = models.BooleanField(default=False)
    rendered_html = models.TextField(editable=False, blank=True)

    def save(self, *args, **kwargs):
        import markdown
        self.rendered_html = markdown.markdown(self.content, extensions=["extra", "codehilite"])
        super().save(*args, **kwargs)


