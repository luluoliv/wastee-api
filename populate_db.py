import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastee.settings')

import django
django.setup()


from api.models import User, Seller, Category, Product, ProductImage, Comment, Order, OrderItem, Favorite, Chat, Message

from django.db import migrations

def remove_duplicate_cpfs(apps, schema_editor):
    Seller = apps.get_model('your_app_name', 'Seller')
    # Use a set to track seen CPFs
    seen_cpfs = set()
    for seller in Seller.objects.all():
        if seller.cpf in seen_cpfs:
            seller.delete()  # or update to make unique
        else:
            seen_cpfs.add(seller.cpf)

class Migration(migrations.Migration):
    dependencies = [
        ('your_app_name', 'previous_migration_name'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_cpfs),
    ]

