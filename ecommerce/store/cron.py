from django.utils import timezone
from datetime import timedelta
from .models import Product


def my_cron_job():
    deadline = timezone.now() - timedelta(days=10)
    unusold_products = Product.objects.filter(
        is_active=True,
        created_at__lt=deadline).exclude(orders__created_at__gte=deadline)

    count = unusold_products.count()
    if count > 0:
        unusold_products.update(is_active=False)
        print("successfully delisted unusold_products")
    else:
        print("no unusold_products found")
