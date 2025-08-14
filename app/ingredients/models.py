from django.db import models
from django.utils import translation
from django.utils.text import slugify

from core.models import UnitChoice


class Category(models.Model):
    wweia_fc_code = models.IntegerField(null=True, blank=True)  # USDA category code
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255)

    class Meta:
        unique_together = ('wweia_fc_code', 'name')

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_translated_name(self):
        """Return the translated name based on the current active language."""
        current_lang = translation.get_language()
        translation_obj = self.translations.filter(language_code=current_lang).first()
        return translation_obj.name if translation_obj else self.name


class CategoryTranslation(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10, default='de')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('category', 'language_code')

    def __str__(self):
        return f"{self.name} ({self.language_code})"


class Nutrient(models.Model):
    """
    Stores static nutrient definition from USDA FDC API.
    Example: Protein (id=1003, unitName='g')
    """
    fdc_nutrient_id = models.IntegerField(unique=True)  # USDA nutrient ID
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=20)  # USDA nutrient number string
    rank = models.IntegerField()
    unit = models.CharField(
        max_length=10,
        choices=UnitChoice.choices,
        default=UnitChoice.GRAM,
    )
    slug = models.SlugField(unique=True, max_length=255)

    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class IngredientNutrient(models.Model):
    """
    Join table storing the amount of a given nutrient for an ingredient.
    """
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='nutrients')
    nutrient = models.ForeignKey('Nutrient', on_delete=models.CASCADE)
    amount = models.FloatField()  # amount per unit (as per USDA data)

    class Meta:
        unique_together = ('ingredient', 'nutrient')

    def __str__(self):
        return f"{self.ingredient.name} - {self.nutrient.name}: {self.amount}{self.nutrient.get_unit_display()}"


class IngredientLookup(models.Model):
    fdc_id = models.IntegerField(unique=True)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Ingredient(models.Model):
    fdc_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('fdc_id', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_translated_name()}"

    def get_translated_name(self):
        """Return the translated name based on the current active language."""
        current_lang = translation.get_language()
        translation_obj = self.translations.filter(language_code=current_lang).first()
        return translation_obj.name if translation_obj else self.name


class IngredientTranslation(models.Model):
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10, default='de')
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('ingredient', 'language_code')

    def __str__(self):
        return f"{self.name} ({self.language_code})"
