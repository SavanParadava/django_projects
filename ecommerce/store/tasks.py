from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from .models import Product

import logging

logger = logging.getLogger(__name__)

@shared_task
def deactivate_unsold_products():
    deadline = timezone.now() - timedelta(days=10)
    
    unsold_products = Product.objects.filter(
        is_active=True,
        created_at__lt=deadline
    ).exclude(orders__created_at__gte=deadline)

    count = unsold_products.count()
    
    if count > 0:
        unsold_products.update(is_active=False)
        cache.delete_pattern("filtered_products_*")
        message = f"Successfully delisted {count} unsold products and filtered cache cleared"
        logger.info(message)
        return message
    else:
        message = "No unsold products found"
        logger.info(message)
        return message