from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

from django.db import transaction
from django.shortcuts import get_object_or_404

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
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

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
    def my_products(self, request):
        store_user = get_object_or_404(StoreUser, original_user_id=request.user.id)
        products = Product.objects.filter(retailer=store_user).order_by('-created_at')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

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
            total_active_products = products.count()
            
            if max_price:
                products = products.filter(price__lte=float(max_price))
            if min_price:
                products = products.filter(price__gte=float(min_price))
            if category_id:
                products = products.filter(category=category_id)
            if search_text:
                products = products.filter(name__icontains=search_text)
            if retailer_id:
                products = products.filter(retailer=retailer_id)
            if sort_by_price=="1":
                products = products.order_by('price')
            elif sort_by_price=="-1":
                products = products.order_by('-price')
            else:
                products = products.order_by('-created_at')
            
            page = self.paginate_queryset(products)
            serializer = ProductSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_active_products'] = total_active_products
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
        product = serializer.instance.product

        quantity = serializer.validated_data['quantity']

        if product.amount_in_stock < quantity:
            raise ValidationError({
                "quantity": [
                    f"Only {product.amount_in_stock} items left in stock."
                ]
            })
        elif quantity <= 0:
            serializer.instance.delete()
        else:
            serializer.save()

    def perform_create(self, serializer):
        product = serializer.validated_data['product']

        quantity = serializer.validated_data['quantity']
        x = Cart.objects.filter(user_id=self.request.user.id, product_id=product.id)
        cart_quantity = x[0].quantity if x else 0

        total_quantity = quantity + cart_quantity

        if product.amount_in_stock == 0:
                raise ValidationError({
                "quantity": [
                    f"Item is out of stock"
                ]
            })
        
        if product.amount_in_stock < total_quantity:
            raise ValidationError({
                "quantity": [
                    f"Only {product.amount_in_stock} items left in stock."
                ]
            })

        serializer.save()

    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        store_user = get_object_or_404(StoreUser, original_user_id=request.user.id)

        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"detail": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        address = get_object_or_404(Address, id=address_id, user=store_user)
        
        cart_items = Cart.objects.filter(user=store_user)
        
        if not cart_items.exists():
            return Response(
                {"detail": "Cart is empty."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product.pk)
                    
                    if product.amount_in_stock < item.quantity:
                        raise ValidationError(
                            f"Insufficient stock for '{product.name}'. Available: {product.amount_in_stock}, Requested: {item.quantity}"
                        )
                for item in cart_items:
                    product = Product.objects.select_for_update().get(pk=item.product.pk)
                    
                    product.amount_in_stock -= item.quantity
                    product.save()
                    
                    Order.objects.create(
                        user=store_user,
                        product=product,
                        quantity=item.quantity,
                        total_amount=product.price * item.quantity,
                        shipping_address=address
                    )
                
                cart_items.delete()
                
            return Response({"detail": "Checkout successful."}, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class LikedProductViewSet(viewsets.ModelViewSet):
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

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Address.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(user_id=self.request.user.id).update(is_default=False)
        serializer.save()
