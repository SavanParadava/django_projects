from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def sync_user_to_store(sender, instance, created, **kwargs):
    if instance.role not in ['CUSTOMER', 'RETAILER']:
        return

    from store.models import StoreUser

    StoreUser.objects.update_or_create(original_user_id=instance.id,
                                       defaults={
                                           'email': instance.email,
                                           'role': instance.role
                                       })


@receiver(post_delete, sender=CustomUser)
def delete_user_from_store(sender, instance, **kwargs):
    from store.models import StoreUser
    try:
        StoreUser.objects.get(original_user_id=instance.id).delete()
    except StoreUser.DoesNotExist:
        pass
