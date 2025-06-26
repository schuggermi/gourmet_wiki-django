from django.contrib import admin

from menus.models import MenuCourse, MenuType, MenuItem, Menu


@admin.register(MenuCourse)
class MenuCourseAdmin(admin.ModelAdmin):
    list_display = ('menu_type', 'course_type', 'order')
    list_filter = ('menu_type',)
    ordering = ('menu_type', 'order')
    search_fields = ('course_type', 'menu_type__name')


class MenuCourseInline(admin.TabularInline):
    model = MenuCourse
    extra = 1
    ordering = ['order']
    fields = ('order', 'course_type')


@admin.register(MenuType)
class MenuTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [MenuCourseInline]
    search_fields = ('name',)


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    autocomplete_fields = ['menu_course', 'recipe']
    fields = ('menu_course', 'recipe')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_type', 'created_at')
    list_filter = ('menu_type',)
    inlines = [MenuItemInline]
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('menu', 'menu_course', 'recipe')
    list_filter = ('menu__menu_type', 'menu_course__course_type')
    autocomplete_fields = ['menu', 'menu_course', 'recipe']
    search_fields = ('menu__name', 'recipe__name', 'menu_course__course_type')
