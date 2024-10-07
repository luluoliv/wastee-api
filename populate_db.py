import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastee.settings')

import django
django.setup()

from api.models import User, ConfirmationCode, Seller, Category, Product, ProductImage, Comment, Order, OrderItem, Favorite, Chat, Message

# Create some users
user1 = User.objects.create_user('user1@example.com', 'password123', name='User  1')
user2 = User.objects.create_user('user2@example.com', 'password123', name='User  2')

# Create some sellers
seller1 = Seller.objects.create(user=user1, address='Address 1', postal_code='12345', state='State 1', city='City 1', neighborhood='Neighborhood 1')
seller2 = Seller.objects.create(user=user2, address='Address 2', postal_code='67890', state='State 2', city='City 2', neighborhood='Neighborhood 2')

# Create some categories
category1 = Category.objects.create(name='Category 1', description='Description 1')
category2 = Category.objects.create(name='Category 2', description='Description 2')

# Create some products
product1 = Product.objects.create(title='Product 1', original_price=10.99, discounted_price=9.99, rate=4.5, description='Description 1', seller=seller1, category=category1)
product2 = Product.objects.create(title='Product 2', original_price=20.99, discounted_price=19.99, rate=4.8, description='Description 2', seller=seller2, category=category2)

# Create some product images
product_image1 = ProductImage.objects.create(product=product1, image_url='https://example.com/image1.jpg')
product_image2 = ProductImage.objects.create(product=product2, image_url='https://example.com/image2.jpg')

# Create some comments
comment1 = Comment.objects.create(product=product1, user=user1, comment='Comment 1', rating=5, date='2022-01-01', time='10:00:00')
comment2 = Comment.objects.create(product=product2, user=user2, comment='Comment 2', rating=4, date='2022-01-02', time='11:00:00')

# Create some orders
order1 = Order.objects.create(user=user1, total_price=20.00, status='pending')
order2 = Order.objects.create(user=user2, total_price=30.00, status='shipped')

# Create some order items
order_item1 = OrderItem.objects.create(order=order1, product=product1, quantity=2, price=10.00)
order_item2 = OrderItem.objects.create(order=order2, product=product2, quantity=3, price=20.00)

# Create some favorites
favorite1 = Favorite.objects.create(user=user1, product=product1)
favorite2 = Favorite.objects.create(user=user2, product=product2)

# Create some chats
chat1 = Chat.objects.create(buyer=user1, seller=seller1, product=product1)
chat2 = Chat.objects.create(buyer=user2, seller=seller2, product=product2)

# Create some messages
message1 = Message.objects.create(chat=chat1, sender=user1, message='Hello!')
message2 = Message.objects.create(chat=chat2, sender=user2, message='Hi!')