# import random
# from django.db import transaction
# from django.contrib.auth import get_user_model
# # Replace 'your_app' with the actual name of your app containing these models
# from store.models import Category, Product, Order, Cart, LikedProduct, Review, StoreUser

# User = get_user_model()

# def populate_data():
#     print("Starting data population...")

#     # 1. Fetch the specific Users
#     # We use get_or_create to ensure the script doesn't fail if they don't exist,
#     # though in your case they likely already do.
#     users_data = [
#         {"email": "cileri6042@gopicta.com", "role": "retailer"},
#         {"email": "heyidig806@ixospace.com", "role": "customer"},
#         {"email": "savanparadava1999@gmail.com", "role": "retailer"},
#         {"email": "cileri5@gopicta.com", "role": "customer"}
#     ]

#     user_objs = []
#     for u_data in users_data:
#         # Assuming username is email or generated from email for this example
#         user= StoreUser.objects.get(email=u_data["email"])
#         user_objs.append(user)
#         print(f"Loaded User: {user.email}")

#     retailer_1 = user_objs[0]
#     customer_1 = user_objs[1]
#     retailer_2 = user_objs[2]
#     customer_2 = user_objs[3]
    
#     # Pool of users for random assignment
#     all_users = [retailer_1, customer_1, retailer_2, customer_2]

#     # 2. Create Categories
#     categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports & Outdoors"]
#     cat_objs = {}
    
#     for cat_name in categories:
#         cat, _ = Category.objects.get_or_create(name=cat_name)
#         cat_objs[cat_name] = cat
#     print(f"Created {len(cat_objs)} Categories.")

#     # 3. Define 50 Products
#     products_data = [
#         # Electronics
#         ("Smartphone X Pro", 999, "Electronics"),
#         ("Noise Cancelling Headphones", 250, "Electronics"),
#         ("4K Ultra HD Monitor", 400, "Electronics"),
#         ("Wireless Mechanical Keyboard", 120, "Electronics"),
#         ("Gaming Mouse RGB", 60, "Electronics"),
#         ("Smart Watch Series 5", 300, "Electronics"),
#         ("Tablet 10-inch Display", 450, "Electronics"),
#         ("Bluetooth Speaker Mini", 45, "Electronics"),
#         ("External SSD 1TB", 110, "Electronics"),
#         ("USB-C Hub Multiport", 35, "Electronics"),
        
#         # Clothing
#         ("Men's Cotton T-Shirt", 20, "Clothing"),
#         ("Slim Fit Jeans", 45, "Clothing"),
#         ("Leather Jacket", 150, "Clothing"),
#         ("Running Sneakers", 80, "Clothing"),
#         ("Summer Floral Dress", 55, "Clothing"),
#         ("Hooded Sweatshirt", 40, "Clothing"),
#         ("Winter Scarf Wool", 25, "Clothing"),
#         ("Denim Shorts", 30, "Clothing"),
#         ("Formal White Shirt", 50, "Clothing"),
#         ("Ankle Socks (3 Pack)", 15, "Clothing"),

#         # Home & Kitchen
#         ("High-Speed Blender", 90, "Home & Kitchen"),
#         ("Ceramic Coffee Mug", 12, "Home & Kitchen"),
#         ("Non-Stick Frying Pan", 35, "Home & Kitchen"),
#         ("Queen Size Bed Sheets", 40, "Home & Kitchen"),
#         ("Memory Foam Pillow", 30, "Home & Kitchen"),
#         ("Automatic Coffee Maker", 75, "Home & Kitchen"),
#         ("Stainless Steel Knife Set", 60, "Home & Kitchen"),
#         ("Robot Vacuum Cleaner", 200, "Home & Kitchen"),
#         ("Desk Lamp LED", 25, "Home & Kitchen"),
#         ("Bath Towel Set", 30, "Home & Kitchen"),

#         # Books
#         ("Python Crash Course", 35, "Books"),
#         ("The Great Gatsby", 15, "Books"),
#         ("Introduction to Algorithms", 80, "Books"),
#         ("Sci-Fi Short Stories", 20, "Books"),
#         ("History of the World", 45, "Books"),
#         ("Modern Cooking Guide", 30, "Books"),
#         ("Self-Improvement 101", 18, "Books"),
#         ("Mystery Novel Vol 1", 12, "Books"),
#         ("Business Strategy Guide", 28, "Books"),
#         ("Travel Guide: Japan", 22, "Books"),

#         # Sports
#         ("Yoga Mat Non-Slip", 25, "Sports & Outdoors"),
#         ("Dumbbell Set (10kg)", 50, "Sports & Outdoors"),
#         ("Protein Shaker Bottle", 10, "Sports & Outdoors"),
#         ("Tennis Racket Pro", 120, "Sports & Outdoors"),
#         ("Basketball Indoor/Outdoor", 35, "Sports & Outdoors"),
#         ("Running Armband", 15, "Sports & Outdoors"),
#         ("Camping Tent (2 Person)", 90, "Sports & Outdoors"),
#         ("Hiking Backpack 40L", 70, "Sports & Outdoors"),
#         ("Resistance Bands Set", 20, "Sports & Outdoors"),
#         ("Swimming Goggles", 18, "Sports & Outdoors"),
#     ]

#     # 4. Insert Products and generate Interactions
#     print("Creating products and interactions...")
    
#     with transaction.atomic():
#         for prod_name, price, cat_name in products_data:
#             product = Product.objects.create(
#                 name=prod_name,
#                 price=price,
#                 amount_in_stock=random.randint(5, 100),
#                 category=cat_objs[cat_name],
#                 retailer=random.choice([retailer_1,retailer_2]),
#                 is_active=True
#             )

#             # --- Generate Random Reviews ---
#             # 30% chance a product has a review
#             if random.random() > 0.7:
#                 reviewer = random.choice([customer_1,customer_2])
#                 # Check if review already exists to obey unique_together
#                 if not Review.objects.filter(user=reviewer, product=product).exists():
#                     Review.objects.create(
#                         user=reviewer,
#                         product=product,
#                         rating=random.randint(3, 5),
#                         comment=f"Great {prod_name}! Really liked the quality."
#                     )

#             # --- Generate Random Cart Items ---
#             # 20% chance product is in someone's cart
#             if random.random() > 0.8:
#                 Cart.objects.create(
#                     user=random.choice([customer_1,customer_2]), # Assign most carts to the customer
#                     product=product,
#                     quantity=random.randint(1, 3)
#                 )

#             # --- Generate Liked Products ---
#             # 20% chance product is liked
#             if random.random() > 0.8:
#                 Liker = random.choice([customer_1,customer_2])
#                 LikedProduct.objects.create(
#                     user=Liker,
#                     product=product
#                 )

#             # --- Generate Orders ---
#             # 10% chance product has been ordered
#             if random.random() > 0.9:
#                 buyer = random.choice([customer_1,customer_2]) # Assign orders primarily to customer
#                 qty = random.randint(1, 2)
#                 Order.objects.create(
#                     user=buyer,
#                     product=product,
#                     quantity=qty,
#                     total_amount=price * qty
#                 )

#     print("Success! Data population complete.")
#     print(f"Total Products: {Product.objects.count()}")
#     print(f"Total Orders: {Order.objects.count()}")
#     print(f"Total Reviews: {Review.objects.count()}")

# # Execute the function
# populate_data()


import os
import random
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from store.models import Category, Product, StoreUser
from PIL import Image, ImageDraw

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data population...")
        populate_data(self)
        self.stdout.write(self.style.SUCCESS("Data population complete!"))

def create_dummy_image():
    # Define path: media/products/dummy.jpg
    media_root = settings.MEDIA_ROOT
    product_img_dir = os.path.join(media_root, 'products')
    os.makedirs(product_img_dir, exist_ok=True)
    
    img_filename = 'dummy.jpg'
    img_path = os.path.join(product_img_dir, img_filename)

    # Only create if it doesn't exist
    if not os.path.exists(img_path):
        print("Generating dummy image...")
        # Create a 600x600 image with a random color
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        image = Image.new('RGB', (600, 600), color=color)
        d = ImageDraw.Draw(image)
        d.text((10,10), "Dummy Product", fill=(255,255,255))
        image.save(img_path)
        print(f"Saved dummy image at: {img_path}")
    
    # Return relative path for DB
    return os.path.join('products', img_filename)

def populate_data(command_instance):
    # 1. Setup Dummy Image
    dummy_image_path = create_dummy_image()

    # 2. Categories
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports", "Toys", "Beauty", "Automotive", "Garden", "Music"]
    cat_objs = []
    for name in categories:
        cat, _ = Category.objects.get_or_create(name=name)
        cat_objs.append(cat)
    print(f"Categories ready: {len(cat_objs)}")

    # 3. Create 1,000 Retailers (CustomUser)
    # We must create them one by one to ensure the 'post_save' signal fires and creates the StoreUser
    current_count = User.objects.filter(role='RETAILER').count()
    needed = 1000 - current_count
    print("here 1")
    
    if needed > 0:
        print(f"Generating {needed} Retailers (this triggers signals)...")
        for i in range(needed):
            email = fake.unique.email()
            
            # Create CustomUser
            # Using User() + set_password() + save() is safer than create_user() if custom managers are tricky
            user = User(
                email=email, 
                role='RETAILER', 
                is_verified=True
            )
            user.set_password('password123')
            user.save() # This triggers the signal to create StoreUser
            
            if (i + 1) % 100 == 0:
                print(f"Created {i + 1} users...")
    print("here 2")
    
    # Fetch StoreUsers (profiles) to assign to products
    # We filter by the role of the related CustomUser
    retailers = list(StoreUser.objects.filter(role='RETAILER'))
    if not retailers:
        print("Error: No StoreUsers found. Check if your signals.py is working correctly.")
        return
    print("here 3")

    # 4. Create 10,000 Products
    print("Generating 10,000 Products (this may take a moment)...")
    products_to_create = []
    
    for i in range(10000):
        products_to_create.append(Product(
            name=fake.catch_phrase(),
            price=round(random.uniform(10.0, 1000.0), 2),
            amount_in_stock=random.randint(0, 500),
            category=random.choice(cat_objs),
            retailer=random.choice(retailers),
            is_active=True,
            image=dummy_image_path
        ))
        
        # Batch insert every 1000 items
        if len(products_to_create) >= 1000:
            Product.objects.bulk_create(products_to_create)
            products_to_create = []
            print(f"Created {i+1} products...")

    if products_to_create:
        Product.objects.bulk_create(products_to_create)