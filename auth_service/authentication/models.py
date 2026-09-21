from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Group(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        DELIVERY_CREW = "DELIVERY CREW", "Delivery Crew"
        CUSTOMER = "CUSTOMER", "Customer"

    group = models.CharField(max_length=20, choices=Group.choices, default=Group.CUSTOMER)

    username = None
    email = models.CharField(max_length=200, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
