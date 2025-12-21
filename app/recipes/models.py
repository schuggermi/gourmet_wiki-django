from collections import OrderedDict
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ingredients.models import Ingredient
from recipes.services.cost_calculator import calculate_recipe_cost

from core.models import CourseTypeChoice, SkillLevelChoice, UnitChoice

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        validators=[MinLengthValidator(3), MaxLengthValidator(50)],
        verbose_name=_("Recipe Name"),
    )
    description = models.TextField(
        blank=True,
        max_length=250,
        verbose_name=_("Description"),
    )
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
    course_type = models.CharField(
        verbose_name=_('Course'),
        max_length=50,
        choices=CourseTypeChoice.choices,
        blank=True,
    )
    portions = models.PositiveIntegerField(
        default=4,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ],
        verbose_name=_('Portions'),
    )
    cooking_time_minutes = models.PositiveIntegerField(
        verbose_name=_('Cooking Time (Minutes)'),
        default=30,
        validators=[
            MinValueValidator(1),
        ]
    )
    skill_level = models.CharField(
        max_length=50,
        choices=SkillLevelChoice.choices,
        verbose_name=_("Skill Level"),
        blank=False,
    )
    favorite_by = models.ManyToManyField(
        User,
        related_name='favorite_recipes',
        blank=True,
    )
    is_published = models.BooleanField(verbose_name=_('Published'), default=False)

    @property
    def total_time_minutes(self):
        return self.cooking_time_minutes  # self.working_time_minutes + self.cooking_time_minutes + self.rest_time_minutes

    @property
    def get_thumbnail_image(self):
        if self.images.exists():
            return self.images.first().image.url
        return settings.STATIC_URL + 'images/placeholder_recipe.png'

    @property
    def get_thumbnail_image_dark(self):
        if self.images.exists():
            return self.images.first().image.url
        return settings.STATIC_URL + 'images/placeholder_recipe.png'

    @property
    def ordered_preparation_steps(self):
        steps = list(self.preparation_steps.all().order_by('order'))
        display_index = 0
        for s in steps:
            if s.is_section:
                setattr(s, 'display_index', None)
            else:
                display_index += 1
                setattr(s, 'display_index', display_index)
        return steps

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(avg=Avg('score'))['avg']
        return round(max(0, avg if avg is not None else 0), 1)

    def __str__(self):
        return self.name

    def is_favorite_by(self, user):
        return self.favorite_by.filter(pk=user.pk).exists()

    def calculate_scaled_ingredients(self, target_portions: int):
        scale_factor = Decimal(target_portions / self.portions)

        scaled_ingredients = []
        for ri in self.ingredients.all():
            scaled_quantity = ri.scale_quantity(scale_factor)
            scaled_ingredients.append({
                'ingredient': ri.ingredient,
                'quantity': scaled_quantity,
                'unit': ri.unit,
            })

        return scaled_ingredients

    def get_nutrients(self):
        ingredients = self.ingredients.all()
        parsed_nutrients = {}

        for ingredient in ingredients:
            nutrients = ingredient.ingredient.nutrients.all()

            for nutrient in nutrients:
                if nutrient.nutrient.fdc_nutrient_id not in parsed_nutrients:
                    parsed_nutrients[nutrient.nutrient.fdc_nutrient_id] = {
                        'name': nutrient.nutrient.name,
                        'amount': nutrient.amount * (float(ingredient.quantity) / 100),
                        'unit': nutrient.nutrient.get_unit_display(),
                    }
                else:
                    parsed_nutrients[nutrient.nutrient.fdc_nutrient_id]['amount'] += nutrient.amount

        sorted_nutrients = OrderedDict(
            sorted(parsed_nutrients.items(), key=lambda item: item[1]['name'])
        )

        return sorted_nutrients


class RecipeRating(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')


class RecipePreparationStep(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="preparation_steps",
        on_delete=models.CASCADE
    )
    step_text = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )
    order = models.PositiveIntegerField()
    is_section = models.BooleanField(
        default=False,
        help_text=_("Marks this row as a section/category break instead of a regular step."),
    )
    section_title = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    def __str__(self):
        if self.is_section:
            return f"[Section] {self.section_title}"
        return f"{self.order + 1}. {self.step_text}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name="ingredients",
        on_delete=models.CASCADE
    )
    name = models.CharField(unique=True, max_length=100)
    slug = models.SlugField(blank=True, max_length=150)
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.1')),
        ],
        verbose_name=_("Quantity"),
    )
    unit = models.CharField(
        max_length=10,
        choices=UnitChoice.choices,
        default=UnitChoice.GRAM,
        verbose_name=_("Unit"),
    )

    class Meta:
        unique_together = ('recipe', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{round(self.quantity, 0)}{self.unit} {self.name}"

    def scale_quantity(self, scale_factor: Decimal):
        quantity = self.quantity * scale_factor
        return round(quantity, 1)


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
