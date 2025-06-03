from django.contrib.auth import get_user_model
from django.db import models

from ingredients.models import Ingredient
from recipes.services.cost_calculator import calculate_recipe_cost

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return calculate_recipe_cost(self)

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
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="z.B. 200 (g oder ml)"
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} {self.ingredient.name} for {self.recipe.name}"
