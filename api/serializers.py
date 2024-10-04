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

        print(f"Tentando autenticar usuário com email: {email}")

        if not email or not password:
            raise serializers.ValidationError('Email e senha são obrigatórios.')

        user = authenticate(email=email, password=password)
        if not user:
            print("Autenticação falhou: Credenciais inválidas")
            raise serializers.ValidationError('Credenciais inválidas.')

        return {'user': user}


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Este email já está em uso.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return value

    def create(self, validated_data):
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

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'discounted_price', 'category', 'images']

    def validate_discounted_price(self, value):
        if value < 0:
            raise ValidationError("O preço com desconto não pode ser negativo.")
        return value

    def validate_title(self, value):
        if Product.objects.filter(title=value).exists():
            raise ValidationError("Um produto com este título já existe.")
        return value


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


