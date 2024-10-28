from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import User, ConfirmationCode, Seller, Category, Product, ProductImage, Comment, Order, OrderItem, Favorite, Chat, Message
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from datetime import date, timedelta

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
    images = ProductImageSerializer(many=True, read_only=True) 
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    chat_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'original_price', 'discounted_price', 'description', 'favorited', 'rate', 
            'seller_id', 'seller_name', 'category_name', 'state', 'city', 'neighborhood', 'images', 'chat_id'
        )

    def get_chat_id(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            chat = Chat.objects.filter(buyer=request.user, seller=obj.seller).first()
            if chat:
                return chat.id
        return None
    
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



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category_id = serializers.IntegerField(write_only=True)
    seller_id = serializers.IntegerField(write_only=True)
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'original_price', 'discounted_price', 'description', 'category_id', 'images', 'seller_id', 'seller_name', 'favorited']

    def validate_images(self, value):
        if len(value) > 6:
            raise serializers.ValidationError("Você pode enviar no máximo 6 imagens.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        category_id = validated_data.pop('category_id')
        seller_id = validated_data.pop('seller_id')

        category = Category.objects.get(id=category_id)
        seller = Seller.objects.get(id=seller_id)

        product = Product.objects.create(category=category, seller=seller, **validated_data)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product


class SellerSerializer(serializers.ModelSerializer):    
    cpf = serializers.CharField(max_length=11, required=True)
    birth_date = serializers.DateField(required=True)
    rg = serializers.ImageField(required=True)
    selfie_document = serializers.ImageField(required=True)
    city = serializers.CharField(max_length=100, required=True)
    state = serializers.CharField(max_length=100, required=True)
    neighborhood = serializers.CharField(max_length=100, required=True)
    postal_code = serializers.CharField(max_length=10, required=True)
    user = UserSerializer(read_only=True) 
    products = ProductSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    chat_id = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = '__all__'

    def validate_cpf(self, value):
        if Seller.objects.filter(cpf=value).exists():
            raise ValidationError("Este CPF já está em uso.")
        return value

    def validate_birth_date(self, value):
        if value >= date.today():
            raise ValidationError("A data de nascimento não pode ser hoje ou uma data futura.")
        return value

    def validate(self, data):
        return data
    
    def get_comments(self, obj):
        products = obj.products.all()
        comments = Comment.objects.filter(product__in=products)
        return CommentSerializer(comments, many=True).data
    
    def get_chat_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            chat = Chat.objects.get(seller=obj, buyer=request.user)
            return chat.id
        except Chat.DoesNotExist:
            return None

    def create(self, validated_data):
        user = validated_data.pop('user') 

        if Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError(f"O user {user.email} já é um vendedor.")
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            raise ValidationError("O usuário com este ID não existe.")
        
        seller = Seller.objects.create(user=user, **{k: v for k, v in validated_data.items() if k != 'user'})
        return seller

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('date', 'time')

    def get_user_name(self, obj):
        return obj.user.name if obj.user else None
    
    def get_formatted_time(self, obj):
        return obj.time.strftime("%H:%M") 

    def create(self, validated_data):
        comment = super().create(validated_data)
        comment.product.update_rating()
        return comment


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
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'message', 'sent_at', 'sender_name']

    def validate(self, data):
        chat = data.get('chat')
        if chat is None:
            raise serializers.ValidationError('Chat deve ser enviado.')

        user = self.context['request'].user

        if user.id != chat.buyer.id and user.id != chat.seller.user.id:
            raise serializers.ValidationError('Você não tem permissão para enviar mensagens neste chat.')

        return data


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.user.name', read_only=True)

    class Meta:
        model = Chat
        fields = ['id','buyer', 'seller', 'seller_name', 'messages', 'started_at', 'last_message']

    def get_last_message(self, obj):
        """Retorna a última mensagem do chat, se existir."""
        last_message = obj.messages.last()  
        if last_message:
            return {
                'id': last_message.id,
                'message': last_message.message,
                'sent_at': last_message.sent_at,  
                'sender_name': last_message.sender.name,
                'sender_id': last_message.sender.id,
            }
        return None
    
    def get_participants(self, obj):
        return [participant.name for participant in obj.participants.all()]

    def validate(self, data):
        buyer = data.get('buyer')
        seller = data.get('seller')

        if not buyer or not seller:
            raise serializers.ValidationError('Um chat deve ter tanto um comprador quanto um vendedor.')

        if buyer == seller.user:  
            raise serializers.ValidationError('O comprador e o vendedor não podem ser a mesma pessoa.')

        return data