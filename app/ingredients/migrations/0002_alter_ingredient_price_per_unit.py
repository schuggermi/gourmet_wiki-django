# Generated by Django 5.2.1 on 2025-06-03 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingredients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='price_per_unit',
            field=models.DecimalField(decimal_places=4, help_text='Price per unit in EUR', max_digits=10),
        ),
    ]
