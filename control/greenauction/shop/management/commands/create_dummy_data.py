import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Product, CustomUser, Order
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def handle(self, *args, **kwargs):
        # Create sellers
        sellers = []
        for i in range(1, 4):
            seller = CustomUser.objects.create_user(
                username=f'seller{i}', 
                email=f'seller{i}@example.com', 
                password='password123', 
                is_seller=True
            )
            sellers.append(seller)
        
        # Create products
        products = [
            {'name': 'Shine Muscat 1', 'price': 20, 'seller': sellers[0]},
            {'name': 'Shine Muscat 2', 'price': 25, 'seller': sellers[1]},
            {'name': 'Shine Muscat 3', 'price': 22, 'seller': sellers[2]},
            {'name': 'Strawberry 1', 'price': 10, 'seller': sellers[0]},
            {'name': 'Strawberry 2', 'price': 12, 'seller': sellers[1]},
            {'name': 'Strawberry 3', 'price': 15, 'seller': sellers[2]},
        ]
        
        for product in products:
            p = Product.objects.create(
                name=product['name'], 
                price=product['price'], 
                seller=product['seller']
            )
            # Create order history for the past week
            for days_ago in range(7):
                order_date = datetime.now() - timedelta(days=days_ago)
                quantity = random.randint(1, 10)
                Order.objects.create(
                    product=p, 
                    buyer=sellers[0],  # Using the first seller as the buyer for simplicity
                    quantity=quantity,
                    total_price=product['price'] * quantity,
                    date_ordered=order_date
                )
        
        self.stdout.write(self.style.SUCCESS('Dummy data created successfully!'))
