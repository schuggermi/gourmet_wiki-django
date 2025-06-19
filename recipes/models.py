from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
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


class SkillLevelChoice(models.TextChoices):
    BEGINNER = 'BEGINNER', _('Beginner')
    INTERMEDIATE = 'INTERMEDIATE', _('Intermediate')
    ADVANCED = 'ADVANCED', _('Advanced')
    PROFESSIONAL = 'PROFESSIONAL', _('Professional')


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=250)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
    )
    portions = models.PositiveIntegerField(
        default=4,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ]
    )
    working_time_hours = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24),
        ]
    )
    working_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(60),
        ]
    )
    cooking_time_hours = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24),
        ]
    )
    cooking_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(60),
        ]
    )
    rest_time_hours = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24),
        ]
    )
    rest_time_minutes = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(60),
        ]
    )
    skill_level = models.CharField(
        max_length=50,
        choices=SkillLevelChoice.choices,
        default=SkillLevelChoice.BEGINNER,
    )

    @property
    def total_cost(self):
        return calculate_recipe_cost(self)

    @property
    def get_thumbnail_image(self):
        if self.thumbnail_image and self.images:
            return self.thumbnail_image
        elif self.thumbnail_image and not self.images:
            return self.thumbnail_image
        elif not self.thumbnail_image and self.images:
            return self.images.first().image
        return settings.MEDIA_URL + 'recipes/images/placeholder.jpg'

    def __str__(self):
        return self.name


class RecipePreparationStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="preparation_steps",
        on_delete=models.CASCADE
    )
    step_text = models.CharField(
        max_length=500,
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order + 1}. {self.step_text}"


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
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    caption = models.CharField(
        max_length=200,
        blank=True
    )
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"Image for {self.recipe.name} - {self.caption}"
