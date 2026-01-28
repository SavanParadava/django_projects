from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from .permissions import *
from .models import *
from .serializers import *

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsRetailer]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        store_user = get_object_or_404(StoreUser, original_user_id=self.request.user.id)
        serializer.save(retailer=store_user)

    @action(detail=False, methods=['get'])
    def filter_products(self, request):
        num = request.query_params.get('num', 9)
        self.paginator.page_size = int(num)
        max_price = request.query_params.get('max_price','')
        min_price = request.query_params.get('min_price','')
        category_id = request.query_params.get('category_id',None)
        retailer_id = request.query_params.get('retailer_id',None)
        search_text = request.query_params.get('search',None)
        sort_by_price = request.query_params.get('sort_by_price',None)

        try:
            products = self.get_queryset()
            
            if max_price:
                products = products.filter(price__lte=float(max_price), is_active=True)
            if min_price:
                products = products.filter(price__gte=float(min_price), is_active=True)
            if category_id:
                products = products.filter(category=category_id, is_active=True)
            if search_text:
                products = products.filter(name__icontains=search_text, is_active=True)
            if retailer_id:
                products = products.filter(retailer=retailer_id, is_active=True)
            if sort_by_price=="1":
                products = products.order_by('price')
            if sort_by_price=="-1":
                products = products.order_by('-price')
            
            page = self.paginate_queryset(products)
            serializer = ProductSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_active_products'] = Product.objects.filter(is_active=True).count()            
            return response
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST)
    
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsCustomer]
    lookup_field = 'product_id'

    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return Cart.objects.filter(user_id=self.request.user.id)
    
    def perform_update(self, serializer):
        quantity = serializer.validated_data.get('quantity')

        if quantity is not None and quantity <= 0:
            serializer.instance.delete()
        else:
            serializer.save()

    def perform_create(self, serializer):
        quantity = serializer.validated_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise ValidationError({"quantity": "Quantity cannot be zero or negative."})
        else:
            serializer.save()
    
class LikedProductViewSet(viewsets.ModelViewSet):
    queryset = LikedProduct.objects.all()
    serializer_class = LikedProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsCustomer]
    lookup_field = 'product_id'

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return LikedProduct.objects.filter(user_id=self.request.user.id)


class ProductReviewsViewSet(viewsets.ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ProductReviewsSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    http_method_names = ['get']

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        
        if product_id:
            return Review.objects.filter(product_id=product_id).order_by('-created_at')
        
        return Review.objects.all().order_by('-created_at')

class EditReviewViewSet(viewsets.ModelViewSet):
    serializer_class = EditReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'product_id'

    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return Review.objects.filter(user_id=self.request.user.id)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsCustomer]

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.id).order_by('-created_at')