from django.contrib import admin
from .models import *

class StoreUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StoreUser._meta.fields]
    search_fields = ("email", "username")
    ordering = ("id",)
    # list_filter = ("is_verified",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]
    search_fields = ("name",)
    ordering = ("id",)

class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
    search_fields = ("name", "category__name", "retailer__email")
    ordering = ("category__name","created_at")
    list_filter = ("category","created_at", "is_active")

class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
    search_fields = ("user__email", "product__name", "id")
    ordering = ("-id",)

class CartAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Cart._meta.fields]
    search_fields = ("user__email", "product__name")
    ordering = ("-created_at",)

class LikedProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LikedProduct._meta.fields]
    search_fields = ("user__email", "product__name")
    ordering = ("product__name",)

class ReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Review._meta.fields]
    search_fields = ("user__email", "product__name", "comment")
    ordering = ("-created_at",)

class AddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Address._meta.fields]
    search_fields = ("user__email", "city__name")

# Register your models here
admin.site.register(StoreUser, StoreUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(LikedProduct, LikedProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Address, AddressAdmin)