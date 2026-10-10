"""
expenses/migrations/0002_seed_categories.py

Data migration: seed the Category table with the default categories
and assign each a distinct color for charts and UI chips.
"""
from django.db import migrations


def seed_categories(apps, schema_editor):
    """Insert the default categories. Uses get_or_create to be idempotent."""
    Category = apps.get_model('expenses', 'Category')

    categories = [
        {'name': 'Food',          'color': '#E63946'},
        {'name': 'Travel',        'color': '#2196F3'},
        {'name': 'Shopping',      'color': '#9C27B0'},
        {'name': 'Bills',         'color': '#FF9800'},
        {'name': 'Entertainment', 'color': '#00BCD4'},
        {'name': 'Health',        'color': '#4CAF50'},
        {'name': 'Education',     'color': '#3F51B5'},
        {'name': 'Groceries',     'color': '#8BC34A'},
        {'name': 'Others',        'color': '#9E9E9E'},
    ]

    for cat in categories:
        Category.objects.get_or_create(name=cat['name'], defaults={'color': cat['color']})


def remove_categories(apps, schema_editor):
    """Reverse migration: remove the seeded categories."""
    Category = apps.get_model('expenses', 'Category')
    names = [
        'Food', 'Travel', 'Shopping', 'Bills',
        'Entertainment', 'Health', 'Education', 'Groceries', 'Others',
    ]
    Category.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
