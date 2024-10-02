from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet,
    UserRegistrationView,
    LoginView,
    ConfirmationCodeView,
    SellerViewSet,
    CategoryViewSet,
    ProductViewSet,
    CommentViewSet,
    OrderViewSet,
    OrderItemViewSet,
    FavoriteViewSet,
    ChatViewSet,
    MessageViewSet,
)

# Definindo o roteamento com DefaultRouter
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'sellers', SellerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'messages', MessageViewSet)

# Definição das URLs usando os viewsets e views específicos
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),  # Cadastro de usuário
    path('login/', LoginView.as_view(), name='token-obtain-pair'),  # Login do usuário
    path('confirm/', ConfirmationCodeView.as_view(), name='confirmation-code'),  # Confirmação do código
    path('', include(router.urls)),  # Inclui as rotas registradas pelo DefaultRouter
]
