from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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

    def list(self, request, *args, **kwargs):
        cache_key = 'all_categories'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        # Cache the categories for 24 hours (86400 seconds)
        cache.set(cache_key, response.data, timeout=86400) 
        return response
    
    # Invalidate (delete) the cache whenever a category is added, updated, or deleted
    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete('all_categories')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.delete('all_categories')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.delete('all_categories')


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Product.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsRetailer]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        store_user = get_object_or_404(StoreUser,
                                       original_user_id=self.request.user.id)
        serializer.save(retailer=store_user)
        cache.delete_pattern("filtered_products_*")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        cache.delete_pattern("filtered_products_*")

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        store_user = get_object_or_404(StoreUser,
                                       original_user_id=request.user.id)
        products = self.get_queryset().filter(
            retailer=store_user).order_by('-created_at')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def filter_products(self, request):
        query_string = request.META.get('QUERY_STRING', '')
        cache_key = f"filtered_products_{query_string}"
        
        # Check if we already have the result for these exact filters in Redis
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
        
        num = request.query_params.get('num', 9)
        self.paginator.page_size = int(num)
        max_price = request.query_params.get('max_price', '')
        min_price = request.query_params.get('min_price', '')
        category_id = request.query_params.get('category_id', None)
        retailer_id = request.query_params.get('retailer_id', None)
        search_text = request.query_params.get('search', None)
        sort_by_price = request.query_params.get('sort_by_price', None)

        try:
            products = self.get_queryset().filter(is_active=True)
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
            if sort_by_price == "1":
                products = products.order_by('price')
            elif sort_by_price == "-1":
                products = products.order_by('-price')
            else:
                products = products.order_by('-created_at')

            page = self.paginate_queryset(products)
            serializer = ProductSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_active_products'] = total_active_products

            # Save the expensive query result to Redis for 10 minutes (600 seconds)
            cache.set(cache_key, response.data, timeout=600)

            return response

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]
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
        if not product.is_active:
            raise ValidationError({
                "active": [
                    f"You can not add product to cart. Product is delisted"
                ]
            })

        quantity = serializer.validated_data['quantity']
        x = Cart.objects.filter(user_id=self.request.user.id,
                                product_id=product.id)
        cart_quantity = x[0].quantity if x else 0

        total_quantity = quantity + cart_quantity

        if product.amount_in_stock == 0:
            raise ValidationError({"quantity": [f"Item is out of stock"]})

        if product.amount_in_stock < total_quantity:
            raise ValidationError({
                "quantity": [
                    f"Only {product.amount_in_stock} items left in stock."
                ]
            })

        serializer.save()

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        try:
            store_user = StoreUser.objects.get(
                original_user_id=request.user.id
            )
        except StoreUser.DoesNotExist:
            return Response(
                {"detail": "Store user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"detail": "Address ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(
                id=address_id,
                user_id=store_user.original_user_id
            )
        except Address.DoesNotExist:
            return Response(
                {"detail": "Address not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 1. Get Cart Items
        cart_items = Cart.objects.filter(user=store_user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic(using='store_db'):
                # 2. Fetch and Lock all products in ONE query
                # We use select_for_update() to lock rows, preventing race conditions.
                product_ids = cart_items.values_list('product_id', flat=True)
                locked_products = Product.objects.select_for_update().in_bulk(
                    product_ids)

                orders_to_create = []
                products_to_update = []

                # 3. Iterate through cart items in memory
                for item in cart_items:
                    product = locked_products.get(item.product_id)

                    if not product:
                        raise ValidationError(
                            f"Product {item.product_id} not found.")

                    # Stock Validation
                    if product.amount_in_stock < item.quantity:
                        raise ValidationError(
                            f"Insufficient stock for '{product.name}'. Available: {product.amount_in_stock}, Requested: {item.quantity}"
                        )

                    # Deduct Stock (in memory)
                    product.amount_in_stock -= item.quantity
                    products_to_update.append(product)

                    # Prepare Order Object (in memory)
                    orders_to_create.append(
                        Order(user=store_user,
                              product=product,
                              quantity=item.quantity,
                              total_amount=product.price * item.quantity,
                              shipping_address=address))

                # 4. Perform Bulk Operations
                # Update all product stocks in 1 SQL query
                Product.objects.bulk_update(products_to_update,
                                            ['amount_in_stock'])

                # Create all orders in 1 SQL query
                Order.objects.bulk_create(orders_to_create)

                # 5. Clear Cart
                cart_items.delete()

            return Response({"detail": "Checkout successful."},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class LikedProductViewSet(viewsets.ModelViewSet):
    serializer_class = LikedProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]
    lookup_field = 'product_id'

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return LikedProduct.objects.filter(user_id=self.request.user.id)


class ProductReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewsSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = StandardResultsSetPagination

    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        # Get the product_id (default to 'all' if none is provided)
        product_id = request.query_params.get('product_id', 'all')
        query_string = request.META.get('QUERY_STRING', '')
        
        # Make the cache key specific to the product
        cache_key = f"reviews_product_{product_id}_{query_string}"
        
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # If not cached, fetch from the database
        response = super().list(request, *args, **kwargs)
        
        # Store in Redis for 15 minutes (900 seconds)
        cache.set(cache_key, response.data, timeout=900)
        
        return response

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)

        if product_id:
            return Review.objects.filter(
                product_id=product_id).order_by('-created_at')

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
    
    def clear_review_cache(self, product_id):
        # Delete caches ONLY for this specific product
        cache.delete_pattern(f"reviews_product_{product_id}_*")
        cache.delete_pattern("reviews_product_all_*")

    def perform_create(self, serializer):
        instance = serializer.save()
        self.clear_review_cache(instance.product_id)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.clear_review_cache(instance.product_id)

    def perform_destroy(self, instance):
        product_id = instance.product_id
        super().perform_destroy(instance)
        self.clear_review_cache(product_id)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id).order_by('-created_at')


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Address.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Address.objects.filter(user_id=self.request.user.id).update(
                is_default=False)
        serializer.save()
