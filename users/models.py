from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import string

# ========================
# User Manager
# ========================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if not password:
            raise ValueError('Password field is required.')
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# ========================
# Custom User Model
# ========================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('inventory_manager', 'Inventory Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.email} ({self.role})"

# ========================
# Dog Profile (for Customers)
# ========================
class DogProfile(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dog_profile')
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)  # Add this
    gender = models.CharField(max_length=10)
    life_stage = models.CharField(max_length=50)
    size = models.CharField(max_length=30)
    coat_type = models.CharField(max_length=50)
    role = models.CharField(max_length=50)  # Add this
    health_considerations = models.TextField(blank=True)

    def __str__(self):
        return f"{self.owner.email}'s dog - {self.name}"

# ========================
# Email Verification Model (OTP)
# ========================
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

class EmailVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20, choices=[('register', 'register'), ('reset', 'reset')])

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
