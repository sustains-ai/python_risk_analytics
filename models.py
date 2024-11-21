from flask_login import UserMixin
from bson import ObjectId
from datetime import datetime, date

# User Model
class User(UserMixin):
    def __init__(self, id=None, email=None, password=None, default_currency='AED'):
        self.id = str(id) if id else None  # Ensure id is a string (ObjectId as string)
        self.email = email
        self.password = password
        self.default_currency = default_currency

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,  # Use ObjectId when storing in MongoDB
            "email": self.email,
            "password": self.password,
            "default_currency": self.default_currency
        }

    @staticmethod
    def from_dict(data):
        return User(
            id=str(data.get("_id")),  # Ensure _id is converted to string
            email=data["email"],
            password=data["password"],
            default_currency=data.get("default_currency", "AED")
        )

    def __repr__(self):
        return f'<User {self.email}>'

# FinanceData Model
class FinanceData:
    def __init__(self, user_id, date, category, amount, currency='AED', notes=None):
        self.user_id = user_id
        self.date = date
        self.category = category
        self.amount = amount
        self.currency = currency
        self.notes = notes

    def to_dict(self):
        if isinstance(self.date, date):
            self.date = datetime.combine(self.date, datetime.min.time())
        return {
            "user_id": self.user_id,
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency,
            "notes": self.notes
        }

    @staticmethod
    def from_dict(data):
        date_value = data["date"]
        if isinstance(date_value, datetime):
            date_value = date_value.date()
        return FinanceData(
            user_id=data["user_id"],
            date=date_value,
            category=data["category"],
            amount=data["amount"],
            currency=data.get("currency", "AED"),
            notes=data.get("notes")
        )

    def __repr__(self):
        return f'<FinanceData {self.category} - {self.amount}>'
