from django.contrib import admin
from .models import Category, Ingredient


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'wweia_fc_code', 'slug')
    search_fields = ('name', 'wweia_fc_code')
    prepopulated_fields = {'slug': ('name',)}


# @admin.register(Nutrient)
# class NutrientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'fdc_nutrient_id', 'number', 'rank', 'unit', 'slug')
#     search_fields = ('name', 'fdc_nutrient_id', 'number')
#     list_filter = ('unit',)
#     prepopulated_fields = {'slug': ('name',)}


# @admin.register(IngredientLookup)
# class IngredientLookupAdmin(admin.ModelAdmin):
#     list_display = ('fdc_id', 'description')
#     search_fields = ('description',)
#     ordering = ('description',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug') # 'fdc_id', 'category'
    search_fields = ('name', ) # 'fdc_id'
    list_filter = () # 'category',
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = () # 'category',


# @admin.register(IngredientNutrient)
# class IngredientNutrientAdmin(admin.ModelAdmin):
#     list_display = ('ingredient', 'nutrient', 'amount')
#     search_fields = ('ingredient__name', 'nutrient__name')
#     list_filter = ('nutrient',)
#     autocomplete_fields = ('ingredient', 'nutrient')


# @admin.register(CategoryTranslation)
# class CategoryTranslationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'language_code', 'category')
#     search_fields = ('name', 'category__name')
#     list_filter = ('language_code',)
#     autocomplete_fields = ('category',)


# @admin.register(IngredientTranslation)
# class IngredientTranslationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'language_code', 'ingredient')
#     search_fields = ('name', 'ingredient__name')
#     list_filter = ('language_code',)
#     autocomplete_fields = ('ingredient',)
