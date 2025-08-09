from django.contrib import admin
from .models import Category, Nutrient, Ingredient, IngredientNutrient, IngredientLookup


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'wweia_fc_code', 'slug')
    search_fields = ('name', 'wweia_fc_code')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Nutrient)
class NutrientAdmin(admin.ModelAdmin):
    list_display = ('name', 'fdc_nutrient_id', 'number', 'rank', 'unit', 'slug')
    search_fields = ('name', 'fdc_nutrient_id', 'number')
    list_filter = ('unit',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(IngredientLookup)
class IngredientLookupAdmin(admin.ModelAdmin):
    list_display = ('fdc_id', 'description')
    search_fields = ('description',)
    ordering = ('description',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'fdc_id', 'category', 'slug')
    search_fields = ('name', 'fdc_id')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category',)


@admin.register(IngredientNutrient)
class IngredientNutrientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'nutrient', 'amount')
    search_fields = ('ingredient__name', 'nutrient__name')
    list_filter = ('nutrient',)
    autocomplete_fields = ('ingredient', 'nutrient')
