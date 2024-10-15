import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastee.settings')

import django
django.setup()

from api.models import User, Seller, Category, Product, ProductImage, Comment, Order, OrderItem, Favorite, Chat, Message

# Create popular categories
popular_categories = [
    {'name': 'Smartphones', 'description': 'Latest smartphones from various brands.'},
    {'name': 'Tablets', 'description': 'Tablets for work and entertainment.'},
    {'name': 'Computadores', 'description': 'Desktops and laptops for all purposes.'},
    {'name': 'Monitores', 'description': 'High-quality monitors for every need.'},
    {'name': 'Impressoras', 'description': 'Printers for home and office use.'},
    {'name': 'Periféricos', 'description': 'Peripherals for enhanced productivity.'},
    {'name': 'Câmeras', 'description': 'Digital cameras for photography enthusiasts.'},
    {'name': 'Videogames', 'description': 'Latest video games and consoles.'},
]

# Create Category instances
for category in popular_categories:
    Category.objects.create(name=category['name'], description=category['description'])

