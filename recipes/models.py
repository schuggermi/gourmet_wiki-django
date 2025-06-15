from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

from ingredients.models import Ingredient
from recipes.services.cost_calculator import calculate_recipe_cost

User = get_user_model()


class UnitChoice(models.TextChoices):
    GRAM = 'g', _('g')
    KILOGRAM = 'kg', _('kg')
    LITER = 'l', _('l')
    MILLILITER = 'ml', _('ml')
    OUNCE = 'oz', _('oz')
    TABLESPOON = 'sp', _('sp')
    TEE_SPOON = 'tes', _('tes')



class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
        default='recipes/images/placeholder.jpg'
    )

    @property
    def total_cost(self):
        return calculate_recipe_cost(self)

    def get_thumbnail_url(self):
        if self.thumbnail_image and hasattr(self.thumbnail_image, 'url'):
            return self.thumbnail_image.url
        return settings.MEDIA_URL + 'recipes/images/placeholder.jpg'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredients",
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="z.B. 200 (g oder ml)"
    )
    unit = models.CharField(
        max_length=10,
        choices=UnitChoice.choices,
        default=UnitChoice.GRAM,
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} {self.ingredient.name} for {self.recipe.name}"


class RecipeImage(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    caption = models.CharField(
        max_length=200,
        blank=True
    )

    def __str__(self):
        return f"Image for {self.recipe.name} - {self.caption}"
