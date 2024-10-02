from rest_framework import viewsets
from .models import User, ConfirmationCode, Seller, Category, Product, Comment, Order, OrderItem, Favorite, Chat, Message
from .serializers import UserSerializer, SellerSerializer, LoginSerializer, CategorySerializer, ProductSerializer, CommentSerializer, OrderSerializer, OrderItemSerializer, FavoriteSerializer, ChatSerializer, MessageSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from time import timezone

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from .utils import gerar_codigo_confirmacao, enviar_codigo_email

from rest_framework.authtoken.models import Token


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        print(f"Dados recebidos para login: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response({'error': 'Usuário inativo. Verifique seu email para confirmação.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)  # This line should work correctly
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        codigo = gerar_codigo_confirmacao(user)
        enviar_codigo_email(user.email, codigo)

        return Response({"message": "Usuário registrado com sucesso. Verifique seu email para confirmação."}, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ConfirmationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('confirmation_code')
        user_id = request.data.get('user_id')

        try:
            confirmation = ConfirmationCode.objects.get(confirmation_code=code, user_id=user_id)
            if confirmation.is_used or confirmation.expiration_time < timezone.now():
                return Response({'error': 'Código de confirmação inválido ou expirado'}, status=status.HTTP_400_BAD_REQUEST)

            user = confirmation.user
            user.is_active = True
            user.save()

            confirmation.is_used = True
            confirmation.save()

            return Response({'message': 'Conta confirmada com sucesso!'}, status=status.HTTP_200_OK)
        except ConfirmationCode.DoesNotExist:
            return Response({'error': 'Código de confirmação não encontrado'}, status=status.HTTP_404_NOT_FOUND)


class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [AllowAny] 

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated] 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated] 

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated] 

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated] 

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Favorite.objects.filter(user=self.request.user)
        return Favorite.objects.none()



class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: 
            return Chat.objects.none() 
        return Chat.objects.filter(buyer=user) | Chat.objects.filter(seller=user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: 
            return Message.objects.none()  
        return Message.objects.filter(chat__buyer=user) | Message.objects.filter(chat__seller=user)


