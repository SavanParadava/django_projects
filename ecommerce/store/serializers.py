from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db import transaction
from rest_framework import serializers
from .models import *

class StoreUserSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source='original_user_id')

    class Meta:
        model = StoreUser
        fields = ['user_id', 'email', 'role']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=True)
    
    retailer_id = serializers.PrimaryKeyRelatedField(
        source='retailer',
        read_only=True)
    
    retailer = StoreUserSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'amount_in_stock', 'category_id', 'category', 'retailer_id', 'image', 'retailer']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_amount_in_stock(self, value):
        if value <= 0:
            raise serializers.ValidationError("Stock cannot be zero or negative.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True)
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id','product_id', 'user', 'product', 'quantity', 'total_amount', 'created_at', 'user_id']
    
    def validate_user(self, value):
        return get_object_or_404(StoreUser,original_user_id=value.id)


class CartSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
        )
        
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)


    class Meta:
        model = Cart
        fields = ['id', 'user', 'product_id', 'quantity', 'product']

    def validate_user(self, value):
        return get_object_or_404(StoreUser,original_user_id=value.id)
    
    def create(self, validated_data):
        quantity = validated_data.pop('quantity')
        with transaction.atomic():
            matching_cart_items = Cart.objects.select_for_update().filter(**validated_data)
            
            if matching_cart_items.exists():
                item = matching_cart_items.first()
                item.quantity += 1
                item.save()
                return item
            
            validated_data["quantity"]=1
            cart_item = Cart.objects.create(**validated_data)
            print(cart_item)
            return cart_item
    
class LikedProductSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=True)
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)

    class Meta:
        model = LikedProduct
        fields = ['id', 'user', 'product_id', 'product']
    
    def validate_user(self, value):
        return get_object_or_404(StoreUser,original_user_id=value.id)

class ProductReviewsSerializer(serializers.ModelSerializer):    
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
    )

    user = StoreUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'product_id', 'rating', 'comment', 'created_at']

class EditReviewSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        # read_only=True
    )
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'user', 'product_id', 'rating', 'comment']
    
    def validate_user(self, value):
        return get_object_or_404(StoreUser,original_user_id=value.id)
    
class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Address
        fields = ['id', 'user', 'street_address', 'city', 'state', 'zip_code', 'country', 'phone_number', 'is_default']
    
    def validate_user(self, value):
        return get_object_or_404(StoreUser, original_user_id=value.id)


    # user_id = serializers.SlugRelatedField(
    #     queryset=StoreUser.objects.all(),
    #     slug_field='original_user_id',
    #     source='user',
    #     write_only=True)
