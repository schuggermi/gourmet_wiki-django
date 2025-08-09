from django.db import models
from django.utils.translation import gettext_lazy as _


class UnitChoice(models.TextChoices):
    PIECE = 'piece', _('piece')
    GRAM = 'g', _('g')
    KILOGRAM = 'kg', _('kg')
    LITER = 'l', _('l')
    MILLILITER = 'ml', _('ml')
    OUNCE = 'oz', _('oz')
    TABLESPOON = 'sp', _('sp')
    TEE_SPOON = 'tes', _('tes')


class CourseTypeChoice(models.TextChoices):
    AMUSE_BOUCHE = 'amuse_bouche', _('Amuse-bouche')
    COLD_STARTER = 'cold_starter', _("Hors d'œuvre")
    SOUP = 'soup', _("Potage")
    FISH = 'fish', _("Poisson")
    HOT_STARTER = 'hot_starter', _("Entrée")
    MAIN = 'main', _("Plat de Résistance")
    SORBET = 'sorbet', _("Sorbet")
    ROAST = 'roast', _("Rôti")
    VEGETABLE = 'vegetable', _("Légumes")
    SALAD = 'salad', _("Salade")
    CHEESE = 'cheese', _("Fromage")
    DESSERT = 'dessert', _("Dessert")
    DIGESTIVE_DRINK = 'digestive_drink', _("Digestif")


class SkillLevelChoice(models.TextChoices):
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')
    PROFESSIONAL = 'professional', _('Professional')
