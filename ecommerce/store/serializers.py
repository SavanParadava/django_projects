from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework import serializers
from .models import *

class StoreUserSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(source='original_user_id')

    class Meta:
        model = StoreUser
        fields = ['user_id', 'email', 'role']

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=True)
    
    retailer_id = serializers.PrimaryKeyRelatedField(
        queryset=StoreUser.objects.all(),
        source='retailer',
        required=True)

    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'amount_in_stock', 'category_id', 'retailer_id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class OrderSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True)
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['product_id', 'user', 'product', 'quantity', 'total_amount']
    
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
        fields = ['id', 'user', 'product_id', 'rating', 'comment']

class EditReviewSerializer(serializers.ModelSerializer):    
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
    )
    
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'user', 'product_id', 'rating', 'comment']
    
    def validate_user(self, value):
        return get_object_or_404(StoreUser,original_user_id=value.id)
    


    # user_id = serializers.SlugRelatedField(
    #     queryset=StoreUser.objects.all(),
    #     slug_field='original_user_id',
    #     source='user',
    #     write_only=True)