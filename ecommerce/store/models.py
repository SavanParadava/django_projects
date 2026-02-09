from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class StoreUser(models.Model):
    original_user_id = models.PositiveIntegerField(unique=True, db_index=True)
    email = models.EmailField()
    role = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.role}: {self.email}"


class Category(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120)
    price = models.FloatField()
    amount_in_stock = models.IntegerField()
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True,
                                 related_name='products')
    retailer = models.ForeignKey(StoreUser,
                                 on_delete=models.CASCADE,
                                 related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    image = models.ImageField(upload_to='products/', blank=True, null=True)

    class Meta:
        unique_together = ('name', 'price', 'category', 'retailer')

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(StoreUser,
                             on_delete=models.CASCADE,
                             to_field='original_user_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1),
                                   name='quantity_at_least_one')
        ]


class LikedProduct(models.Model):
    user = models.ForeignKey(StoreUser,
                             on_delete=models.CASCADE,
                             to_field='original_user_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')


class Review(models.Model):
    user = models.ForeignKey(StoreUser,
                             on_delete=models.CASCADE,
                             to_field='original_user_id',
                             related_name='reviews')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5")
    comment = models.TextField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')


class Address(models.Model):
    user = models.ForeignKey(StoreUser,
                             on_delete=models.CASCADE,
                             to_field='original_user_id',
                             related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street_address}, {self.city}"


class Order(models.Model):
    user = models.ForeignKey(StoreUser,
                             on_delete=models.CASCADE,
                             to_field='original_user_id',
                             related_name='orders')
    product = models.ForeignKey(Product,
                                on_delete=models.PROTECT,
                                related_name='orders')
    quantity = models.PositiveIntegerField()
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)
    shipping_address = models.ForeignKey(Address,
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)

    def __str__(self):
        return f"{self.user.email}: {self.product.name}"
