from django.core.management.base import BaseCommand
from django.db import transaction
from decouple import config

from authentication.models import User

SEED_USERS = [
    ("manager@restaurant.local", User.Group.MANAGER),
    ("crew@restaurant.local", User.Group.DELIVERY_CREW),
    ("customer@restaurant.local", User.Group.CUSTOMER),
]


class Command(BaseCommand):
    help = "Create one demo user per group. Skips users that already exist."

    @transaction.atomic
    def handle(self, *args, **options):
        password = config("SEED_PASSWORD", default="restaurant123")

        for email, group in SEED_USERS:
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"{email} already exists, skipping")
                continue

            User.objects.create_user(email=email, password=password, group=group)
            self.stdout.write(self.style.SUCCESS(f"Created {email} ({group})"))