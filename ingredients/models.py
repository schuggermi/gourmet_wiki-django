from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(
        max_length=20,
        help_text="e.g. g, ml, piece(s)"
    )

    def __str__(self):
        return f"{self.name} ({self.unit})"
