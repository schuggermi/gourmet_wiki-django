# Generated by Django 5.2.1 on 2025-06-04 23:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipe_thumbnail_image_recipeimage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeimage',
            options={},
        ),
        migrations.RemoveField(
            model_name='recipeimage',
            name='order',
        ),
    ]
