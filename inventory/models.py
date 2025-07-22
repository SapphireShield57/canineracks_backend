from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

# ==========================
# Choices for categories
# ==========================

MAIN_CATEGORIES = [
    ('Food', 'Food'),
    ('Treat', 'Treat'),
    ('Health', 'Health'),
    ('Grooming', 'Grooming'),
    ('Wellness', 'Wellness'),
]

SUB_CATEGORIES = [
    ('Dry', 'Dry'), ('Wet', 'Wet'), ('Raw', 'Raw'),
    ('Dental', 'Dental'), ('Training', 'Training'),
    ('Vitamins', 'Vitamins'), ('Tick & Flea', 'Tick & Flea'),
    ('Recovery Collars', 'Recovery Collars'),
    ('Shampoo & Conditioner', 'Shampoo & Conditioner'),
    ('Pet Brush', 'Pet Brush'), ('Spritz & Wipes', 'Spritz & Wipes'),
    ('Toys', 'Toys'), ('Beds & Kennels', 'Beds & Kennels'),
    ('Harness & Leashes', 'Harness & Leashes'),
]

# ==========================
# Product Model
# ==========================

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    purchased_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_purchased = models.DateField()
    supplier_name = models.CharField(max_length=255)

    main_category = models.CharField(max_length=50, choices=MAIN_CATEGORIES)
    sub_category = models.CharField(max_length=50, choices=SUB_CATEGORIES)

    # Recommendation-based dog suitability code
    product_code = models.CharField(max_length=30)

    image = CloudinaryField('image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.product_code}"

# ==========================
# Stock History Model
# ==========================

class StockHistory(models.Model):
    ACTION_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('update', 'Updated'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.action} ({self.quantity_changed}) @ {self.timestamp}"


User = get_user_model()

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
