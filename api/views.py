import logging
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.decorators import action

from .models import (
    User, ConfirmationCode, Seller, Category, Product,
    Comment, Order, OrderItem, Favorite, Chat, Message
)
from .serializers import (
    UserSerializer, LoginSerializer, CategorySerializer,
    ProductDetailSerializer, CommentSerializer, OrderSerializer,
    OrderItemSerializer, FavoriteSerializer, ChatSerializer,
    MessageSerializer, SellerSerializer, ProductSerializer
)
from .utils import gerar_codigo_confirmacao, enviar_email_oauth

logger = logging.getLogger(__name__)

class YourClassName:
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Dados recebidos para login: {request.data}")
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(f"Erro de validação no login: {e.detail}")
            return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']

        if not user.is_active:
            return Response({'error': 'Usuário inativo. Verifique seu email para confirmação.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        user_data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'created_at': user.created_at,
            'user_type': user.user_type,
        }

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        }, status=status.HTTP_200_OK)

class LogoutView(TokenBlacklistView):
    permission_classes = [IsAuthenticated]

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)

        codigo = gerar_codigo_confirmacao(user)

        try:
            enviar_email_oauth(user.email, codigo)
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            user.delete()  # Deletar o usuário se o email falhar
            return Response({"error": "Erro ao enviar e-mail. Tente novamente mais tarde."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Usuário registrado com sucesso. Verifique seu email para confirmação."}, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            user.delete()
            return Response({'message': 'Usuário deletado com sucesso!'}, status=status.HTTP_204_NO_CONTENT)
        except IntegrityError:
            return Response({'error': 'Não é possível deletar o usuário com registros relacionados existentes.'}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('confirmation_code')
        email = request.data.get('email')
        logger.info(f"Recebido código: {code} para o e-mail: {email}")

    
        confirmation = ConfirmationCode.objects.get(confirmation_code=code, user__email=email)
        if confirmation.is_used or confirmation.expiration_time < timezone.now():
            return Response({'error': 'Código de confirmação inválido ou expirado'}, status=status.HTTP_400_BAD_REQUEST)
        confirmation.is_used = True
        confirmation.save()
        user = confirmation.user
        user.is_active = True
        user.save()

class ConfirmationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('confirmation_code')
        email = request.data.get('email')
        logger.info(f"Recebido código: {code} para o e-mail: {email}")

        try:
            confirmation = ConfirmationCode.objects.get(confirmation_code=code, user__email=email)
            if confirmation.is_used or confirmation.expiration_time < timezone.now():
                return Response({'error': 'Código de confirmação inválido ou expirado'}, status=status.HTTP_400_BAD_REQUEST)

            confirmation.is_used = True
            confirmation.save()

            user = confirmation.user
            user.is_active = True
            user.save()

            return Response({'message': 'Código de confirmação validado com sucesso!', 'user_id': user.id}, status=status.HTTP_200_OK)
        except ConfirmationCode.DoesNotExist:
            logger.error(f"Código de confirmação não encontrado para o e-mail: {email}")
            return Response({'error': 'Código de confirmação não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class SetPasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        password = request.data.get('password')

        if not password:
            return Response({'error': 'A senha é necessária'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(password)
        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Senha definida com sucesso!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        seller = serializer.save()
        
        rg_file = request.FILES.get('rg') 
        selfie_file = request.FILES.get('selfie_document') 

        if rg_file:
            seller.rg.save(rg_file.name, rg_file) 
        if selfie_file:
            seller.selfie_document.save(selfie_file.name, selfie_file) 
            
        user = seller.user  
        user.user_type = 'seller'
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        seller = get_object_or_404(Seller, user_id=user_id)
        serializer = self.get_serializer(seller)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated] 

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        search = self.request.query_params.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class ProductDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        product = self.get_object()
        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        
        if len(images) > 6:
            return Response({'error': 'Você pode enviar no máximo 6 imagens.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.save()

        for image in images:
            product.images.create(image=image)

        return Response({'message': 'Produto criado com sucesso!', 'product': serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Produto atualizado com sucesso!', 'product': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'message': 'Produto removido com sucesso!'}, status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        seller_id = self.request.query_params.get('seller_id')

        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)

        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        product = comment.product
        self.update_product_rating(product)

        return Response({'message': 'Comentário adicionado com sucesso!', 'comment': serializer.data}, status=status.HTTP_201_CREATED)

    def update_product_rating(self, product):
        comments = Comment.objects.filter(product=product)
        if comments.exists():
            average_rating = comments.aggregate(Avg('rating'))['rating__avg']
            product.rate = average_rating
            product.save()

    def list(self, request, *args, **kwargs):
        product_id = self.request.query_params.get('product_id')
        queryset = self.queryset.filter(product_id=product_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({'message': 'Pedido criado com sucesso!', 'order_id': order.id}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
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
        return Favorite.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        favorites = self.get_queryset()
        product_ids = favorites.values_list('product_id', flat=True)

        products = Product.objects.filter(id__in=product_ids, favorited=True)

        serializer = ProductDetailSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']

        if Favorite.objects.filter(user=request.user, product=product).exists():
            return Response({'error': 'Este produto já está nos favoritos.'}, status=status.HTTP_400_BAD_REQUEST)

        favorite = serializer.save()
        product.favorited = True
        product.save()

        product.refresh_from_db()
        updated_product_serializer = ProductDetailSerializer(product)

        logger.info(f"Produto {favorite.product.title} adicionado aos favoritos pelo usuário {request.user.email}.")
        return Response({
            'message': 'Produto adicionado aos favoritos com sucesso!',
            'favorite': serializer.data,
            'product': updated_product_serializer.data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        user = request.user

        try:
            favorite = Favorite.objects.get(user=user, product_id=product_id)
            favorite.delete()

            product = Product.objects.get(id=product_id)
            product.favorited = False
            product.save()
            product.refresh_from_db()
            updated_product_serializer = ProductDetailSerializer(product)

            return Response({
                'detail': 'Produto removido dos favoritos.',
                'product': updated_product_serializer.data
            }, status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({'detail': 'Produto não encontrado nos favoritos.'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'detail': 'Produto não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Chat.objects.none()

        try:
            seller = Seller.objects.get(user=user)
        except Seller.DoesNotExist:
            seller = None
        
        return Chat.objects.filter(buyer=user) | Chat.objects.filter(seller=seller)

    def create(self, request, *args, **kwargs):
        buyer_id = request.data.get('buyer')
        seller_id = request.data.get('seller')
        existing_chat = Chat.objects.filter(buyer_id=buyer_id, seller_id=seller_id).first()

        if existing_chat:
            return Response({
                'error': 'Um chat já existe entre esse comprador e vendedor.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = serializer.save()

        return Response({
            'message': 'Chat criado com sucesso!',
            'chat': ChatSerializer(chat).data
        }, status=status.HTTP_201_CREATED)
    
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

        