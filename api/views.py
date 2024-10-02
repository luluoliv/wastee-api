from rest_framework import viewsets
from .models import User, ConfirmationCode, Seller, Category, Product, Comment, Order, OrderItem, Favorite, Chat, Message
from .serializers import UserSerializer, ConfirmationCodeSerializer, SellerSerializer, CategorySerializer, ProductSerializer, CommentSerializer, OrderSerializer, OrderItemSerializer, FavoriteSerializer, ChatSerializer, MessageSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from time import timezone
from rest_framework_simplejwt.views import TokenObtainPairView


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConfirmationCodeView(APIView):
    def post(self, request):
        code = request.data.get('confirmation_code')
        user_id = request.data.get('user_id')

        try:
            confirmation = ConfirmationCode.objects.get(confirmation_code=code, user_id=user_id)
            if confirmation.is_used or confirmation.expiration_time < timezone.now():
                return Response({'error': 'Invalid or expired confirmation code'}, status=status.HTTP_400_BAD_REQUEST)

            user = confirmation.user
            user.is_active = True
            user.save()
            confirmation.is_used = True
            confirmation.save()

            return Response({'message': 'Account confirmed successfully!'}, status=status.HTTP_200_OK)
        except ConfirmationCode.DoesNotExist:
            return Response({'error': 'Confirmation code not found'}, status=status.HTTP_404_NOT_FOUND)

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
