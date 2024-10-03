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

from rest_framework.response import Response
from rest_framework import status

from .utils import gerar_codigo_confirmacao, enviar_codigo_email

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"Dados recebidos para login: {request.data}")
        serializer = self.get_serializer(data=request.data)
        
        try:
            user = serializer.is_valid(raise_exception=True) 
        except ValidationError as e:
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        if not user.is_active:
            return Response({'error': 'Usuário inativo. Verifique seu email para confirmação.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)



class LogoutView(TokenBlacklistView):
    permission_classes = [AllowAny]


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

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        search = self.request.query_params.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def create(self, request, *args, **kwargs):
        """Criação de produto com validação específica para vendedores."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response({'message': 'Produto criado com sucesso!', 'product': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Atualiza um produto e fornece mensagens específicas."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Produto atualizado com sucesso!', 'product': serializer.data}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        """Adiciona um novo comentário a um produto."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response({'message': 'Comentário adicionado com sucesso!', 'comment': serializer.data}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Lista os comentários de um produto específico."""
        product_id = self.request.query_params.get('product_id')
        queryset = self.queryset.filter(product_id=product_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        """Criação de um novo pedido."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({'message': 'Pedido criado com sucesso!', 'order_id': order.id}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Obtém os detalhes de um pedido específico."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    def create(self, request, *args, **kwargs):
        """Adiciona um produto aos favoritos."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        favorite = serializer.save()
        return Response({'message': 'Produto adicionado aos favoritos com sucesso!', 'favorite': serializer.data}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Remove um produto dos favoritos."""
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Produto removido dos favoritos com sucesso!'}, status=status.HTTP_204_NO_CONTENT)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: 
            return Chat.objects.none() 
        return Chat.objects.filter(buyer=user) | Chat.objects.filter(seller=user)

    def create(self, request, *args, **kwargs):
        """Inicia um novo chat entre comprador e vendedor."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()
        return Response({'message': 'Chat iniciado com sucesso!', 'chat_id': chat.id}, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated: 
            return Message.objects.none()  
        return Message.objects.filter(chat__buyer=user) | Message.objects.filter(chat__seller=user)

    def create(self, request, *args, **kwargs):
        """Envia uma nova mensagem em um chat."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response({'message': 'Mensagem enviada com sucesso!', 'message': serializer.data}, status=status.HTTP_201_CREATED)



