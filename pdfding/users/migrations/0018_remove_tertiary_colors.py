# Generated by Django 5.1.7 on 2025-04-04 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_add_annotation_sorting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='custom_theme_color_tertiary_1',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='custom_theme_color_tertiary_2',
        ),
    ]
