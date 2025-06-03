from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(
        max_length=20,
        help_text="e.g. g, ml, piece(s)"
    )
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Price per unit in EUR",
    )

    def __str__(self):
        return f"{self.name} ({self.unit})"
