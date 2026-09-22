from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    cuisine = models.CharField(max_length=255)

class Menu(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='menu/items/', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=450)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
