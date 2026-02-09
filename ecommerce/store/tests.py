from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .models import StoreUser, Category, Product, Cart, Order, Address

User = get_user_model()


class EcommerceTestCase(APITestCase):
    databases = {'default', 'store_db'}

    def setUp(self):
        # 1. Setup Users
        self.retailer_user = User.objects.create_user(username='retailer',
                                                      email='r@e.com',
                                                      password='password123',
                                                      role='RETAILER')
        self.customer_user = User.objects.create_user(username='customer',
                                                      email='c@e.com',
                                                      password='password123',
                                                      role='CUSTOMER')

        # 2. Get StoreUsers (synced via signals)
        self.retailer_store_user = StoreUser.objects.get(
            original_user_id=self.retailer_user.id)
        self.customer_store_user = StoreUser.objects.get(
            original_user_id=self.customer_user.id)

        # 3. Data
        self.category = Category.objects.create(name="Tech")
        # CHANGED: Set stock to 50 to accommodate the checkout test that buys 10 items
        self.product = Product.objects.create(name="GPU",
                                              price=500.0,
                                              amount_in_stock=50,
                                              category=self.category,
                                              retailer=self.retailer_store_user)

    def get_token_headers(self, user):
        self.client.force_authenticate(user=user)
        return {}

    # ----------------------------------------------------------------
    # Product Tests
    # ----------------------------------------------------------------

    def test_retailer_can_create_product(self):
        """Ensure a Retailer can create a product"""
        self.get_token_headers(self.retailer_user)
        data = {
            "name": "Gaming Mouse",
            "price": 50.0,
            "amount_in_stock": 100,
            "category_id": self.category.id,
            "is_active": True
        }
        response = self.client.post('/api/store/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.filter(name="Gaming Mouse").count(), 1)

    def test_customer_cannot_create_product(self):
        """Ensure a Customer cannot create a product (Permission Check)"""
        self.get_token_headers(self.customer_user)
        data = {
            "name": "Hacker Laptop",
            "price": 1000.0,
            "amount_in_stock": 10,
            "category_id": self.category.id
        }
        response = self.client.post('/api/store/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_stock_validation(self):
        """Ensure product cannot be created with negative stock"""
        self.get_token_headers(self.retailer_user)
        data = {
            "name": "Bad Product",
            "price": 50.0,
            "amount_in_stock": -5,
            "category_id": self.category.id
        }
        response = self.client.post('/api/store/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------
    # Cart Tests
    # ----------------------------------------------------------------

    def test_add_to_cart_fresh(self):
        """Test adding a new item to the cart"""
        self.get_token_headers(self.customer_user)
        data = {"product_id": self.product.id, "quantity": 2}

        response = self.client.post('/api/store/cart/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Cart.objects.filter(user=self.customer_store_user).count(), 1)
        self.assertEqual(Cart.objects.get().quantity, 2)

    def test_add_duplicate_item_merges_quantity(self):
        """Test that adding the same product twice updates quantity (Your Logic Check)"""
        self.get_token_headers(self.customer_user)

        # 1. Add 2 items
        self.client.post('/api/store/cart/', {
            "product_id": self.product.id,
            "quantity": 2
        })
        # 2. Add 3 MORE items
        self.client.post('/api/store/cart/', {
            "product_id": self.product.id,
            "quantity": 3
        })

        # Verify: Should be 1 Cart Item with quantity 5
        cart_items = Cart.objects.filter(user=self.customer_store_user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 5)

    def test_add_to_cart_exceeds_stock(self):
        """Test validation when trying to add more items than available"""
        # Create limited stock product
        limited_p = Product.objects.create(name="Rare Item",
                                           price=500,
                                           amount_in_stock=1,
                                           category=self.category,
                                           retailer=self.retailer_store_user)

        self.get_token_headers(self.customer_user)
        data = {"product_id": limited_p.id, "quantity": 5}

        response = self.client.post('/api/store/cart/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cart_quantity(self):
        """Test updating cart quantity via PATCH"""
        # Initial Add
        cart_item = Cart.objects.create(user=self.customer_store_user,
                                        product=self.product,
                                        quantity=1)

        self.get_token_headers(self.customer_user)
        response = self.client.patch(f'/api/store/cart/{self.product.id}/',
                                     {'quantity': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    # ----------------------------------------------------------------
    # Address & Checkout Tests
    # ----------------------------------------------------------------

    def test_address_creation_links_correctly(self):
        """Test that Address is linked to StoreUser automatically (Your Logic Check)"""
        self.get_token_headers(self.customer_user)
        data = {
            "street_address": "123 Python Way",
            "city": "Django",
            "state": "TS",
            "zip_code": "12345",
            "country": "Testland",
            "phone_number": "1234567890"
        }
        response = self.client.post('/api/store/addresses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        address = Address.objects.get(id=response.data['id'])
        self.assertEqual(address.user, self.customer_store_user)

    def test_checkout_process(self):
        """Full flow: Add Address -> Add to Cart -> Checkout -> Verify Order & Stock"""
        self.get_token_headers(self.customer_user)

        # 1. Create Address
        addr = Address.objects.create(user=self.customer_store_user,
                                      street_address="A",
                                      city="B",
                                      state="C",
                                      zip_code="D",
                                      country="E",
                                      phone_number="F")

        # 2. Add to Cart (Qty: 10)
        Cart.objects.create(user=self.customer_store_user,
                            product=self.product,
                            quantity=10)

        # 3. Checkout
        response = self.client.post('/api/store/cart/checkout/',
                                    {"address_id": addr.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. Verifications
        self.assertEqual(
            Cart.objects.filter(user=self.customer_store_user).count(),
            0)  # Cart Empty
        self.assertEqual(
            Order.objects.filter(user=self.customer_store_user).count(),
            1)  # Order Created
        self.product.refresh_from_db()
        self.assertEqual(self.product.amount_in_stock, 40)  # 50 - 10 = 40

    def test_checkout_insufficient_stock_race_simulation(self):
        """Simulate stock dropping before checkout completes"""
        self.get_token_headers(self.customer_user)

        addr = Address.objects.create(user=self.customer_store_user,
                                      street_address="A",
                                      city="B",
                                      state="C",
                                      zip_code="D",
                                      country="E",
                                      phone_number="F")

        # User adds 50 (all stock) to cart
        Cart.objects.create(user=self.customer_store_user,
                            product=self.product,
                            quantity=50)

        # Suddenly stock drops to 10 (simulating another purchase)
        self.product.amount_in_stock = 10
        self.product.save()

        # Checkout should fail
        response = self.client.post('/api/store/cart/checkout/',
                                    {"address_id": addr.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_products(self):
        """Test the custom filter_products action"""
        Product.objects.create(name="Cheap",
                               price=10,
                               amount_in_stock=10,
                               category=self.category,
                               retailer=self.retailer_store_user)

        self.get_token_headers(self.customer_user)
        response = self.client.get(
            '/api/store/products/filter_products/?max_price=20')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(p['name'] == "Cheap" for p in response.data['results']))

    # ----------------------------------------------------------------
    # Standard Logic Tests
    # ----------------------------------------------------------------

    def test_add_duplicate_item_merges_quantity(self):
        """Test that adding the same product twice updates quantity (Your Bulk Logic)"""
        self.get_token_headers(self.customer_user)

        # Add 2 items
        self.client.post('/api/store/cart/', {
            "product_id": self.product.id,
            "quantity": 2
        })
        # Add 3 MORE items
        self.client.post('/api/store/cart/', {
            "product_id": self.product.id,
            "quantity": 3
        })

        # Verify: 1 row, 5 qty
        cart_items = Cart.objects.filter(user=self.customer_store_user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 5)

    def test_checkout_success(self):
        """Test happy path checkout"""
        self.get_token_headers(self.customer_user)

        # Create Address & Cart
        addr = Address.objects.create(user=self.customer_store_user,
                                      street_address="A",
                                      city="B",
                                      state="C",
                                      zip_code="D",
                                      country="E",
                                      phone_number="F")
        Cart.objects.create(user=self.customer_store_user,
                            product=self.product,
                            quantity=2)

        # Checkout
        response = self.client.post('/api/store/cart/checkout/',
                                    {"address_id": addr.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assertions
        self.product.refresh_from_db()
        self.assertEqual(self.product.amount_in_stock,
                         48)  # CHANGED: 50 - 2 = 48
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Cart.objects.count(), 0)

    # ----------------------------------------------------------------
    # Sequential "Race" Condition (SQLite Safe)
    # ----------------------------------------------------------------

    def test_last_item_contention(self):
        """
        Simulate User A buying the last item before User B.
        No threads needed; just verifying state checks works.
        """
        # Set stock to 1
        self.product.amount_in_stock = 1
        self.product.save()

        # Create User B
        user_b = User.objects.create_user(username='user_b',
                                          email='b@test.com',
                                          password='pw',
                                          role='CUSTOMER')
        store_user_b = StoreUser.objects.get(original_user_id=user_b.id)

        # Address for both
        addr_a = Address.objects.create(user=self.customer_store_user,
                                        street_address="A",
                                        city="A",
                                        state="A",
                                        zip_code="1",
                                        country="A",
                                        phone_number="1")
        addr_b = Address.objects.create(user=store_user_b,
                                        street_address="B",
                                        city="B",
                                        state="B",
                                        zip_code="2",
                                        country="B",
                                        phone_number="2")

        # Both add 1 to cart
        Cart.objects.create(user=self.customer_store_user,
                            product=self.product,
                            quantity=1)
        Cart.objects.create(user=store_user_b, product=self.product, quantity=1)

        # User A Checkouts -> Success
        self.get_token_headers(self.customer_user)
        resp_a = self.client.post('/api/store/cart/checkout/',
                                  {"address_id": addr_a.id})
        self.assertEqual(resp_a.status_code, status.HTTP_201_CREATED)

        # User B Checkouts -> Fail (Stock is now 0)
        self.get_token_headers(user_b)
        resp_b = self.client.post('/api/store/cart/checkout/',
                                  {"address_id": addr_b.id})

        self.assertEqual(resp_b.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Insufficient stock", str(resp_b.data))

    # ----------------------------------------------------------------
    # Transaction Safety (Atomic Rollback)
    # ----------------------------------------------------------------

    def test_checkout_rollback_on_failure(self):
        """
        CRITICAL: This proves 'atomic' works without threads.
        We simulate a crash AFTER stock is deducted but BEFORE orders are created.
        The DB should roll back the stock deduction.
        """
        self.get_token_headers(self.customer_user)

        addr = Address.objects.create(user=self.customer_store_user,
                                      street_address="X",
                                      city="Y",
                                      state="Z",
                                      zip_code="0",
                                      country="K",
                                      phone_number="9")
        Cart.objects.create(user=self.customer_store_user,
                            product=self.product,
                            quantity=5)

        initial_stock = self.product.amount_in_stock  # 50

        # We force an error during Order creation (which happens AFTER stock update in your view)
        # Your view: 1. bulk_update(product) -> 2. bulk_create(order)
        with patch('store.models.Order.objects.bulk_create') as mock_create:
            mock_create.side_effect = Exception("Simulated Database Crash!")

            response = self.client.post('/api/store/cart/checkout/',
                                        {"address_id": addr.id})

            # 1. Expect failure
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("Simulated Database Crash", str(response.data))

            # 2. Verify Rollback
            # If atomic failed, stock would be 45 (50 - 5).
            # If atomic worked, stock should still be 50.
            self.product.refresh_from_db()
            self.assertEqual(
                self.product.amount_in_stock, initial_stock,
                "FAIL: Transaction did not roll back stock update after order creation failed."
            )

            # 3. Cart should still exist (it wasn't deleted because of rollback)
            self.assertEqual(
                Cart.objects.filter(user=self.customer_store_user).count(), 1)

    # ----------------------------------------------------------------
    # Security & Privacy Tests (Crucial for E-commerce)
    # ----------------------------------------------------------------

    def test_user_cannot_see_others_orders(self):
        """
        Security Check: User A should NOT be able to list or retrieve User B's orders.
        """
        # 1. Setup: Create an order for User B (The Victim)
        user_b = User.objects.create_user(username='victim',
                                          email='v@test.com',
                                          password='pw',
                                          role='CUSTOMER')
        store_user_b = StoreUser.objects.get(original_user_id=user_b.id)

        order_b = Order.objects.create(user=store_user_b,
                                       product=self.product,
                                       quantity=1,
                                       total_amount=100.0,
                                       shipping_address=Address.objects.create(
                                           user=store_user_b,
                                           street_address="B St",
                                           city="B",
                                           state="B",
                                           zip_code="2",
                                           country="B",
                                           phone_number="2"))

        # 2. Action: User A (The Attacker) tries to list orders
        self.get_token_headers(self.customer_user)  # Login as User A
        response = self.client.get(
            '/api/store/orders/'
        )  # Assuming you have an OrderViewSet at this URL

        # 3. Verify: The list should be empty (or not contain order_b)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0,
                         "Security Fail: User A can see User B's orders!")

    def test_user_cannot_access_others_address(self):
        """
        Security Check: User A should NOT be able to view/edit User B's address.
        """
        # 1. Setup: User B has an address
        user_b = User.objects.create_user(username='neighbor',
                                          email='n@test.com',
                                          password='pw',
                                          role='CUSTOMER')
        store_user_b = StoreUser.objects.get(original_user_id=user_b.id)
        addr_b = Address.objects.create(user=store_user_b,
                                        street_address="Secret St",
                                        city="Hidden",
                                        state="H",
                                        zip_code="0",
                                        country="X",
                                        phone_number="0")

        # 2. Action: User A tries to GET User B's address ID
        self.get_token_headers(self.customer_user)
        response = self.client.get(f'/api/store/addresses/{addr_b.id}/')

        # 3. Verify: Should be 404 Not Found (Standard DRF behavior for filtered querysets)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
