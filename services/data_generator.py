import json
import random
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict
import os

fake = Faker('en_IN')

class FinancialDataGenerator:
    def __init__(self):
        self.categories = {
            "Food": ["Swiggy", "Zomato", "McDonald's", "Dominos", "Starbucks", "Local Restaurant"],
            "Shopping": ["Amazon", "Flipkart", "Big Basket", "DMart", "Myntra", "Ajio"],
            "Rent": ["Monthly Rent", "House Rent", "Apartment Rent"],
            "Salary": ["Monthly Salary", "Salary Credit", "Income"],
            "Utilities": ["Electricity Bill", "Water Bill", "Internet Bill", "Mobile Recharge", "Gas Bill"],
            "Entertainment": ["Netflix", "Amazon Prime", "BookMyShow", "Spotify", "Movie Ticket"],
            "Travel": ["Uber", "Ola", "Rapido", "Petrol", "Train Ticket", "Flight Booking"],
            "Others": ["ATM Withdrawal", "Bank Charges", "Insurance", "Medical", "Groceries"]
        }
        
        self.transaction_id_counter = 1
    
    def generate_description(self, category: str, merchant: str, trans_type: str) -> str:
        """Generate realistic transaction description"""
        if trans_type == "Credit":
            if category == "Salary":
                return f"Salary credited by {fake.company()}"
            else:
                return f"Refund from {merchant}"
        else:
            payment_methods = ["UPI payment to", "Card payment at", "Net banking transfer to"]
            return f"{random.choice(payment_methods)} {merchant}"
    
    def generate_transactions_for_user(self, user_id: str, num_transactions: int) -> List[Dict]:
        """Generate transactions for a single user"""
        transactions = []
        
        # Starting balance
        balance = random.randint(50000, 200000)
        
        # Generate dates for the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        for _ in range(num_transactions):
            # Random date
            days_ago = random.randint(0, 180)
            transaction_date = (end_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            # Random category and merchant
            category = random.choice(list(self.categories.keys()))
            merchant = random.choice(self.categories[category])
            
            # Determine transaction type
            if category == "Salary":
                trans_type = "Credit"
                amount = random.randint(50000, 150000)
            else:
                # 90% debit, 10% credit (refunds)
                trans_type = "Debit" if random.random() > 0.1 else "Credit"
                
                if category == "Rent":
                    amount = random.randint(8000, 25000)
                elif category == "Shopping":
                    amount = random.randint(500, 5000)
                elif category == "Food":
                    amount = random.randint(100, 1500)
                elif category == "Utilities":
                    amount = random.randint(200, 3000)
                elif category == "Entertainment":
                    amount = random.randint(200, 1000)
                elif category == "Travel":
                    amount = random.randint(50, 2000)
                else:
                    amount = random.randint(100, 3000)
            
            # Update balance
            if trans_type == "Credit":
                balance += amount
            else:
                balance -= amount
            
            # Create transaction
            transaction = {
                "id": f"txn_{self.transaction_id_counter}",
                "userId": user_id,
                "date": transaction_date,
                "description": self.generate_description(category, merchant, trans_type),
                "amount": amount,
                "type": trans_type,
                "category": category,
                "balance": max(balance, 0)  # Ensure balance doesn't go negative
            }
            
            transactions.append(transaction)
            self.transaction_id_counter += 1
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        return transactions
    
    def generate_data(self, num_users: int = 3, transactions_per_user: int = 150) -> List[Dict]:
        """Generate complete dataset"""
        all_transactions = []
        
        for i in range(1, num_users + 1):
            user_id = f"user_{i}"
            user_transactions = self.generate_transactions_for_user(user_id, transactions_per_user)
            all_transactions.extend(user_transactions)
        
        return all_transactions
    
    def save_to_json(self, transactions: List[Dict], file_path: str):
        """Save transactions to JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated {len(transactions)} transactions saved to {file_path}")


if __name__ == "__main__":
    from config.settings import settings
    
    generator = FinancialDataGenerator()
    transactions = generator.generate_data(
        num_users=settings.NUM_USERS,
        transactions_per_user=settings.TRANSACTIONS_PER_USER
    )
    generator.save_to_json(transactions, settings.DATA_PATH)