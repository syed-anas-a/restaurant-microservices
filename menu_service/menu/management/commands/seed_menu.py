from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, Menu

from decimal import Decimal



SEED_MENU = {
    ("Starters", "Indian"): [
        ("Paneer Tikka", "249.00", "Cottage cheese cubes marinated in spiced yogurt, chargrilled with peppers and onions"),
        ("Chicken 65", "279.00", "Crisp fried chicken tossed with curry leaves, green chillies and red chilli"),
        ("Hara Bhara Kebab", "199.00", "Pan-seared patties of spinach, green peas and potato with mint chutney"),
        ("Tandoori Mushroom", "229.00", "Button mushrooms marinated in tandoori masala and roasted in the clay oven"),
        ("Fish Amritsari", "319.00", "Gram-flour battered fish fillets fried with carom seeds and chaat masala"),
        ("Samosa Chaat", "149.00", "Crushed samosas topped with chickpea curry, yogurt, tamarind and mint chutneys"),
    ],
    ("Main Course", "Indian"): [
        ("Butter Chicken", "349.00", "Tandoori chicken simmered in a rich tomato, butter and cream gravy"),
        ("Paneer Butter Masala", "299.00", "Cottage cheese in a smooth, mildly sweet tomato and cashew gravy"),
        ("Dal Makhani", "249.00", "Black lentils and kidney beans slow-cooked overnight with butter and cream"),
        ("Hyderabadi Chicken Biryani", "379.00", "Dum-cooked basmati rice layered with spiced chicken, saffron and fried onions"),
        ("Vegetable Biryani", "279.00", "Fragrant basmati rice cooked with seasonal vegetables and whole spices"),
        ("Mutton Rogan Josh", "429.00", "Kashmiri-style lamb curry with dried ginger, fennel and Kashmiri chilli"),
    ],
    ("Desserts", "Continental"): [
        ("Chocolate Brownie", "179.00", "Warm fudgy brownie served with a scoop of vanilla ice cream"),
        ("New York Cheesecake", "249.00", "Baked cream cheese cake on a buttery biscuit base with berry compote"),
        ("Tiramisu", "269.00", "Coffee-soaked ladyfingers layered with mascarpone cream and cocoa"),
        ("Crème Brûlée", "229.00", "Vanilla custard with a crisp caramelised sugar crust"),
        ("Gulab Jamun", "129.00", "Milk-solid dumplings soaked in cardamom and rose sugar syrup"),
        ("Mango Kulfi", "149.00", "Dense frozen milk dessert flavoured with Alphonso mango and pistachio"),
    ],
    ("Beverages", "Global"): [
        ("Masala Chai", "79.00", "Tea brewed with milk, cardamom, ginger and cinnamon"),
        ("Filter Coffee", "89.00", "South Indian decoction coffee with frothed hot milk"),
        ("Sweet Lassi", "119.00", "Chilled whisked yogurt drink with a hint of cardamom"),
        ("Fresh Lime Soda", "99.00", "Freshly squeezed lime with soda, served sweet or salted"),
        ("Cold Coffee", "149.00", "Blended iced coffee with milk and a scoop of vanilla ice cream"),
        ("Mint Mojito", "159.00", "Muddled mint and lime topped with soda and crushed ice, non-alcoholic"),
    ],
}


class Command(BaseCommand):
    help = "Seed the menu with sample categories and items. Skips rows that already exist."

    @transaction.atomic
    def handle(self, *args, **options):
        created_categories = 0
        created_items = 0

        for (category_name, cuisine), items in SEED_MENU.items():
            category, category_created = Category.objects.get_or_create(
                name=category_name,
                defaults={"cuisine": cuisine},
            )
            created_categories += category_created

            for title, price, description in items:
                _, item_created = Menu.objects.get_or_create(
                    title=title,
                    defaults={
                        "price": Decimal(price),
                        "description": description,
                        "category": category,
                    },
                )
                created_items += item_created

        self.stdout.write(self.style.SUCCESS(
            f"Menu seeded: {created_categories} new categories, {created_items} new items"
        ))