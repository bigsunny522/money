import datetime
from collections import defaultdict
import calendar

class Account:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def add_transaction(self, amount):
        self.balance += amount

class Transaction:
    def __init__(self, amount, category, date, payment_method):
        self.amount = amount
        self.category = category
        self.date = date
        self.payment_method = payment_method

class Subscription:
    def __init__(self, name, amount, payment_day, payment_method):
        self.name = name
        self.amount = amount
        self.payment_day = payment_day
        self.payment_method = payment_method

class BudgetApp:
    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.subscriptions = []
        self.categories = defaultdict(float)

    def add_account(self, name, balance=0):
        self.accounts[name] = Account(name, balance)

    def add_transaction(self, amount, category, date, payment_method):
        transaction = Transaction(amount, category, date, payment_method)
        self.transactions.append(transaction)
        self.accounts[payment_method].add_transaction(-amount)
        self.categories[category] += amount

    def add_subscription(self, name, amount, payment_day, payment_method):
        subscription = Subscription(name, amount, payment_day, payment_method)
        self.subscriptions.append(subscription)

    def process_subscriptions(self, year, month):
        for sub in self.subscriptions:
            date = datetime.date(year, month, sub.payment_day)
            self.add_transaction(-sub.amount, "Subscription", date, sub.payment_method)

    def get_monthly_summary(self, year, month):
        start_date = datetime.date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime.date(year, month, last_day)

        monthly_transactions = [t for t in self.transactions if start_date <= t.date <= end_date]
        total_income = sum(t.amount for t in monthly_transactions if t.amount > 0)
        total_expense = sum(t.amount for t in monthly_transactions if t.amount < 0)

        category_breakdown = defaultdict(float)
        for t in monthly_transactions:
            if t.amount < 0:
                category_breakdown[t.category] += abs(t.amount)

        return {
            "total_income": total_income,
            "total_expense": abs(total_expense),
            "net": total_income - abs(total_expense),
            "category_breakdown": dict(category_breakdown)
        }

    def get_account_balances(self):
        return {name: account.balance for name, account in self.accounts.items()}

    def get_future_balance(self, account_name, months=1):
        current_balance = self.accounts[account_name].balance
        future_date = datetime.date.today() + datetime.timedelta(days=30*months)
        future_transactions = [t for t in self.transactions if t.date <= future_date and t.payment_method == account_name]
        future_balance = current_balance + sum(t.amount for t in future_transactions)
        return future_balance