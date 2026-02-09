from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import StoreUser, Category, Product, Cart, Order, Address

User = get_user_model()

class EcommerceTestCase(APITestCase):
    # CRITICAL: Ensures tests can access both databases
    databases = {'default', 'store_db'}

    def setUp(self):
        # 1. Create Users (Auth Level)
        self.retailer_user = User.objects.create_user(
            username='retailer', 
            email='retailer@example.com', 
            password='password123',
            role='RETAILER'
        )
        self.customer_user = User.objects.create_user(
            username='customer', 
            email='customer@example.com', 
            password='password123',
            role='CUSTOMER'
        )

        # 2. Fetch StoreUsers (Created automatically via signals)
        self.retailer_store_user = StoreUser.objects.get(original_user_id=self.retailer_user.id)
        self.customer_store_user = StoreUser.objects.get(original_user_id=self.customer_user.id)

        # 3. Create Basic Data (Category & Product)
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Widget", 
            price=100.0, 
            amount_in_stock=50, 
            category=self.category, 
            retailer=self.retailer_store_user
        )

    def get_token_headers(self, user):
        """Helper to force authenticate"""
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
            "name": "Hacker Laptop", "price": 1000.0, 
            "amount_in_stock": 10, "category_id": self.category.id
        }
        response = self.client.post('/api/store/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_stock_validation(self):
        """Ensure product cannot be created with negative stock"""
        self.get_token_headers(self.retailer_user)
        data = {
            "name": "Bad Product", "price": 50.0, 
            "amount_in_stock": -5, "category_id": self.category.id
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
        self.assertEqual(Cart.objects.filter(user=self.customer_store_user).count(), 1)
        self.assertEqual(Cart.objects.get().quantity, 2)

    def test_add_duplicate_item_merges_quantity(self):
        """Test that adding the same product twice updates quantity (Your Logic Check)"""
        self.get_token_headers(self.customer_user)
        
        # 1. Add 2 items
        self.client.post('/api/store/cart/', {"product_id": self.product.id, "quantity": 2})
        # 2. Add 3 MORE items
        self.client.post('/api/store/cart/', {"product_id": self.product.id, "quantity": 3})

        # Verify: Should be 1 Cart Item with quantity 5
        cart_items = Cart.objects.filter(user=self.customer_store_user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 5)

    def test_add_to_cart_exceeds_stock(self):
        """Test validation when trying to add more items than available"""
        # Create limited stock product
        limited_p = Product.objects.create(
            name="Rare Item", price=500, amount_in_stock=1, 
            category=self.category, retailer=self.retailer_store_user
        )

        self.get_token_headers(self.customer_user)
        data = {"product_id": limited_p.id, "quantity": 5}
        
        response = self.client.post('/api/store/cart/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cart_quantity(self):
        """Test updating cart quantity via PATCH"""
        # Initial Add
        cart_item = Cart.objects.create(
            user=self.customer_store_user, product=self.product, quantity=1
        )

        self.get_token_headers(self.customer_user)
        response = self.client.patch(
            f'/api/store/cart/{self.product.id}/', 
            {'quantity': 5}
        )
        
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
            "street_address": "123 Python Way", "city": "Django", 
            "state": "TS", "zip_code": "12345", 
            "country": "Testland", "phone_number": "1234567890"
        }
        response = self.client.post('/api/store/addresses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        address = Address.objects.get(id=response.data['id'])
        self.assertEqual(address.user, self.customer_store_user)

    def test_checkout_process(self):
        """Full flow: Add Address -> Add to Cart -> Checkout -> Verify Order & Stock"""
        self.get_token_headers(self.customer_user)
        
        # 1. Create Address
        addr = Address.objects.create(
            user=self.customer_store_user, street_address="A", city="B", 
            state="C", zip_code="D", country="E", phone_number="F"
        )

        # 2. Add to Cart (Qty: 10)
        Cart.objects.create(user=self.customer_store_user, product=self.product, quantity=10)

        # 3. Checkout
        response = self.client.post('/api/store/cart/checkout/', {"address_id": addr.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. Verifications
        self.assertEqual(Cart.objects.filter(user=self.customer_store_user).count(), 0) # Cart Empty
        self.assertEqual(Order.objects.filter(user=self.customer_store_user).count(), 1) # Order Created
        self.product.refresh_from_db()
        self.assertEqual(self.product.amount_in_stock, 40) # 50 - 10 = 40

    def test_checkout_insufficient_stock_race_simulation(self):
        """Simulate stock dropping before checkout completes"""
        self.get_token_headers(self.customer_user)
        
        addr = Address.objects.create(
            user=self.customer_store_user, street_address="A", city="B", state="C", zip_code="D", country="E", phone_number="F"
        )
        
        # User adds 50 (all stock) to cart
        Cart.objects.create(user=self.customer_store_user, product=self.product, quantity=50)

        # Suddenly stock drops to 10 (simulating another purchase)
        self.product.amount_in_stock = 10
        self.product.save()

        # Checkout should fail
        response = self.client.post('/api/store/cart/checkout/', {"address_id": addr.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_products(self):
        """Test the custom filter_products action"""
        Product.objects.create(name="Cheap", price=10, amount_in_stock=10, category=self.category, retailer=self.retailer_store_user)

        self.get_token_headers(self.customer_user)
        response = self.client.get('/api/store/products/filter_products/?max_price=20')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p['name'] == "Cheap" for p in response.data['results']))