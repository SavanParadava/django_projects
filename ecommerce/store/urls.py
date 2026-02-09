from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart',CartViewSet, basename='cart')
router.register(r'liked_product',LikedProductViewSet, basename='liked-product')
router.register(r'reviews',ProductReviewsViewSet, basename='product-reviews')
router.register(r'user_review',EditReviewViewSet, basename='user-product-review')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [path('', include(router.urls)),]