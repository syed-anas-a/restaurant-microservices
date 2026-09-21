from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ["email"]
    list_display = ["email", "group", "is_staff"]
    
    # Remove username references from admin forms
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Info", {"fields": ("group",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2", "group")}),
    )

admin.site.register(User, CustomUserAdmin)
