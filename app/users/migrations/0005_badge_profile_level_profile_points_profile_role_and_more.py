# Generated by Django 5.2.1 on 2025-07-29 22:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_skill_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.ImageField(blank=True, null=True, upload_to='badges/icons/')),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='profile',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('guest', 'Gast'), ('member', 'Mitglied'), ('author', 'Autor:in'), ('expert', 'Expert:in'), ('curator', 'Kurator:in'), ('admin', 'Admin')], default='member', max_length=20),
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.badge')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badges', to='users.profile')),
            ],
            options={
                'unique_together': {('profile', 'badge')},
            },
        ),
    ]
