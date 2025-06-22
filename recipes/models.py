from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

from ingredients.models import Ingredient
from recipes.services.cost_calculator import calculate_recipe_cost

User = get_user_model()


class UnitChoice(models.TextChoices):
    PIECE = 'piece', _('piece')
    GRAM = 'g', _('g')
    KILOGRAM = 'kg', _('kg')
    LITER = 'l', _('l')
    MILLILITER = 'ml', _('ml')
    OUNCE = 'oz', _('oz')
    TABLESPOON = 'sp', _('sp')
    TEE_SPOON = 'tes', _('tes')


class SkillLevelChoice(models.TextChoices):
    BEGINNER = _('Beginner')
    INTERMEDIATE = _('Intermediate')
    ADVANCED = _('Advanced')
    PROFESSIONAL = _('Professional')


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
    favorite_by = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True,
    )

    @property
    def total_cost(self):
        return calculate_recipe_cost(self)

    @property
    def total_time_hours(self):
        return self.working_time_hours + self.cooking_time_hours + self.rest_time_hours

    @property
    def total_time_minutes(self):
        return self.working_time_minutes + self.cooking_time_minutes + self.rest_time_minutes

    @property
    def get_thumbnail_image(self):
        if self.images.exists():
            return self.images.first().image.url
        return settings.STATIC_URL + 'images/placeholder_recipe.jpg'

    @property
    def ordered_preparation_steps(self):
        return self.preparation_steps.all().order_by('order')

    def __str__(self):
        return self.name

    def is_favorite_by(self, user):
        return self.favorite_by.filter(pk=user.pk).exists()

    def calculate_scaled_ingredients(self, target_portions: int):
        scale_factor = Decimal(target_portions / self.portions)

        scaled_ingredients = []
        for ri in self.ingredients.all():
            scaled_quantity = ri.quantity * scale_factor
            scaled_ingredients.append({
                'ingredient': ri.ingredient,
                'quantity': round(scaled_quantity, 2),
                'unit': ri.unit,
            })

        return scaled_ingredients


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
    quantity = models.PositiveIntegerField(
        default=4,
        validators=[
            MinValueValidator(1),
        ]
    )
    unit = models.CharField(
        max_length=10,
        choices=UnitChoice.choices,
        default=UnitChoice.GRAM,
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{round(self.quantity, 0)}{self.ingredient.unit} {self.ingredient.name}"


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
