from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Cart

@receiver(post_save, sender=Product)
def delete_product_from_cart(sender, instance, created, **kwargs):
    if not created and not instance.is_active:
        Cart.objects.filter(product=instance).delete()