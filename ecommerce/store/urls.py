from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'cart',CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reviews',ProductReviewsViewSet, basename='product-reviews')
router.register(r'liked_product',LikedProductViewSet, basename='liked-product')
router.register(r'user_review',EditReviewViewSet, basename='user-product-review')

urlpatterns = [path('', include(router.urls)),]