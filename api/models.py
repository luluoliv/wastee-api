from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password) 
        else:
            user.password = self.make_random_password()  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default='defaultpassword')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email


class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class Product(models.Model):
    title = models.CharField(max_length=255)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    description = models.TextField()
    favorited = models.BooleanField(default=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=255)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')])
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    favorited_at = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    buyer = models.ForeignKey(User, related_name='buyer', on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, related_name='seller', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
