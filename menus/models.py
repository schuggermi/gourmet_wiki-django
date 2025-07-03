from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from recipes.models import Recipe


class MenuCourse(models.Model):
    menu = models.ForeignKey('Menu', related_name='courses', on_delete=models.CASCADE)
    course_type = models.CharField(max_length=50, choices=Recipe._meta.get_field('course_type').choices)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('menu', 'course_type')
        ordering = ['order']

    def __str__(self):
        return f"{self.menu.name} - {self.get_course_type_display()}"


class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    portions = models.PositiveIntegerField(
        default=4,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_time_hours(self):
        return sum([menu_item.recipe.total_time_hours for menu_item in self.items.all()])

    def total_time_minutes(self):
        return sum([menu_item.recipe.total_time_minutes for menu_item in self.items.all()])

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, related_name='items', on_delete=models.CASCADE)
    menu_course = models.ForeignKey(MenuCourse, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('menu', 'menu_course')  # Enforce one recipe per course in a menu

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.recipe.course_type != self.menu_course.course_type:
            raise ValidationError(
                f"Recipe course type '{self.recipe.course_type}' does not match required '{self.menu_course.course_type}'."
            )
