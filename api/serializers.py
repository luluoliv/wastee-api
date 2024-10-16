from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User, ConfirmationCode, Seller, Category, Product, ProductImage, Comment, Order, OrderItem, Favorite, Chat, Message
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Email e senha são obrigatórios.')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Credenciais inválidas.')

        return {'user': user}

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'user_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Este email já está em uso.")
        return value

    def validate_password(self, value):
        if value and len(value) < 8: 
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return value

    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class ConfirmationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmationCode
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

    def validate_user(self, value):
        if not isinstance(value, User): 
            raise ValidationError("O usuário fornecido não é válido.")
        if Seller.objects.filter(user=value).exists(): 
            raise ValidationError("Este usuário já é um vendedor.")
        return value

    def create(self, validated_data):
        user = validated_data['user']
        return super().create(validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductListSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'original_price', 'discounted_price', 'favorited', 'rate', 'seller_name', 'image'
        )

    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'original_price', 'discounted_price', 'description', 'favorited', 'rate', 
            'seller_id', 'seller_name', 'category_name', 'state', 'city', 'neighborhood', 'image'
        )

    def get_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None

    def validate_discounted_price(self, value):
        price = self.instance.original_price if self.instance else self.initial_data.get('original_price')
        if price is not None and value > price:
            raise serializers.ValidationError("O preço com desconto não pode ser maior que o preço original.")
        if value < 0:
            raise serializers.ValidationError("O preço com desconto não pode ser negativo.")
        return value

    def validate_title(self, value):
        if Product.objects.exclude(id=self.instance.id).filter(title=value).exists() if self.instance else Product.objects.filter(title=value).exists():
            raise serializers.ValidationError("Um produto com este título já existe.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category_id = serializers.IntegerField(write_only=True)
    seller_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'original_price', 'discounted_price', 'description', 'category_id', 'images', 'seller_id']

    def validate_images(self, value):
        if len(value) > 6:
            raise serializers.ValidationError("Você pode enviar no máximo 6 imagens.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        category_id = validated_data.pop('category_id')
        seller_id = validated_data.pop('seller_id')  # Retrieve seller_id from validated data

        # Fetch the related category and seller
        category = Category.objects.get(id=category_id)
        seller = Seller.objects.get(id=seller_id)

        # Create the Product instance
        product = Product.objects.create(category=category, seller=seller, **validated_data)

        # Create ProductImage instances
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'], product=data['product']).exists():
            raise serializers.ValidationError('Este produto já está nos favoritos.')
        return data

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']

    def validate(self, data):
        chat = data['chat']
        user = self.context['request'].user
        if user not in chat.participants.all():
            raise ValidationError('Você não pode enviar mensagens neste chat.')
        return data

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'created_at', 'messages']

    def validate(self, data):
        participants = data['participants']
        if len(participants) < 2:
            raise ValidationError('Um chat deve ter pelo menos dois participantes.')
        return data
