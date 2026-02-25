import threading
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import connections
from .models import StoreUser, Category, Product, Cart, Address
from rest_framework.test import APIClient

User = get_user_model()

class ConcurrentCheckoutTestCase(TransactionTestCase):
    # Allow test to access both DB definitions
    databases = {'default', 'store_db'}

    def setUp(self):
        # 1. Create Retailer & Category
        self.category = Category.objects.create(name="Tech")
        self.retailer = User.objects.create_user(
            username='ret', email='r@t.com', password='pw', role='RETAILER'
        )
        # FIX: get_or_create to prevent signal misfires
        self.r_store, _ = StoreUser.objects.get_or_create(
            original_user_id=self.retailer.id,
            defaults={'email': self.retailer.email, 'role': 'RETAILER'}
        )
        
        # 2. Create Product with STOCK = 1
        self.product = Product.objects.create(
            name="Hot GPU", 
            price=500, 
            amount_in_stock=1, 
            category=self.category, 
            retailer=self.r_store
        )
    
    def test_concurrent_checkout_mass_race(self):
        """
        Simulate 10 users trying to buy the SAME single item at the exact same time.
        """
        NUM_BUYERS = 10
        threads = []
        results = []
        
        # ADDED: A barrier ensures no thread executes the API call 
        # until ALL 10 threads are ready and waiting.
        start_barrier = threading.Barrier(NUM_BUYERS)
        
        print(f"\n[Postgres] Creating {NUM_BUYERS} buyers...")
        
        user_data = []
        for i in range(NUM_BUYERS):
            user = User.objects.create_user(
                username=f'buyer_{i}', email=f'b{i}@t.com', password='pw', role='CUSTOMER'
            )
            # FIX: get_or_create
            store_user, _ = StoreUser.objects.get_or_create(
                original_user_id=user.id,
                defaults={'email': user.email, 'role': 'CUSTOMER'}
            )
            token = str(RefreshToken.for_user(user).access_token)
            
            Cart.objects.create(user=store_user, product=self.product, quantity=1)
            addr = Address.objects.create(
                user=store_user, street_address=f"St {i}", city="C", 
                state="S", zip_code="Z", country="C", phone_number="1"
            )
            user_data.append({'token': token, 'addr_id': addr.id})

        # Force sync before threads start
        for conn in connections.all():
            conn.close()

        def attempt_buy(token, addr_id):
            # 🔥 WAITING AT THE STARTING LINE:
            # This pauses the thread until all 10 threads arrive here
            start_barrier.wait() 
            
            try:
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
                response = client.post(
                    "/api/store/cart/checkout/",
                    {"address_id": addr_id},
                    format="json"
                )
                results.append(response.status_code)
            finally:
                # 🔥 VERY IMPORTANT
                for conn in connections.all():
                    conn.close()

        print("Starting True Race...")
        for data in user_data:
            t = threading.Thread(target=attempt_buy, args=(data['token'], data['addr_id']))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()

        print(f"\nFinal Race Results: {results}")

        success_count = results.count(201)
        fail_400 = results.count(400)
        fail_409 = results.count(409)
        fail_500 = results.count(500)

        total_clean_fails = fail_400 + fail_409
        expected_fails = NUM_BUYERS - 1

        print(f"DEBUG: Success={success_count}, 400s={fail_400}, 409s={fail_409}, 500s={fail_500}")

        # 1. Stock must be exactly 0 (no negative stock!)
        self.product.refresh_from_db()
        self.assertEqual(self.product.amount_in_stock, 0)

        # 2. Exactly one winner
        self.assertEqual(success_count, 1, "There should be exactly one 201 response")

        # 3. All others must be clean (400 or 409)
        self.assertEqual(total_clean_fails, expected_fails, 
                         f"Found {fail_500} unhandled 500 errors! Results: {results}")