from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet,
    UserRegistrationView,
    LoginView,
    LogoutView,
    ConfirmationCodeView,
    SellerViewSet,
    CategoryViewSet,
    ProductViewSet,
    ProductDetailView,
    CommentViewSet,
    OrderViewSet,
    OrderItemViewSet,
    FavoriteViewSet,
    ChatViewSet,
    MessageViewSet,
    SetPasswordView
)

# Definindo o roteamento com DefaultRouter
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'sellers', SellerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'favorites', FavoriteViewSet)
router.register(r'chats', ChatViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'products', ProductViewSet)


urlpatterns = [
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-registration'), 
    path('login/', LoginView.as_view(), name='token-obtain-pair'), 
    path('logout/', LogoutView.as_view(), name='token-obtain-pair'), 
    path('set-password/<int:pk>/', SetPasswordView.as_view(), name='set-password'),
    path('confirm/', ConfirmationCodeView.as_view(), name='confirmation-code'),  
    path('', include(router.urls)),
]
