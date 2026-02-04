from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from .models import Product

class Command(BaseCommand):
    help = "Run scheduled jobs"

    def handle(self, *args, **kwargs):
        deadline = timezone.now() - timedelta(days=10)
    	unusold_products = Product.objects.filter(is_active=True, created_at__lt=deadline).exclude(orders__created_at__gte=deadline)

    	count = unusold_products.count()
    	if count > 0:
        	unusold_products.update(is_active=False)
        	self.stdout.write(self.style.SUCCESS(f'Successfully delisted {count} stale products.'))
    	else:
        	self.stdout.write(self.style.SUCCESS('No stale products found.'))
        print("Jobs executed")
