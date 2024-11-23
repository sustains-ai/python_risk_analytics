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

# Portfolio Model
class Portfolio:
    def __init__(self, id=None, user_id=None, name=None, description=None, created_at=None):
        self.id = str(id) if id else None  # Ensure id is a string (ObjectId as string)
        self.user_id = str(user_id) if user_id else None
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "user_id": ObjectId(self.user_id) if self.user_id else None,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Portfolio(
            id=str(data.get("_id")),
            user_id=str(data.get("user_id")),
            name=data.get("name"),
            description=data.get("description"),
            created_at=data.get("created_at")
        )

    def __repr__(self):
        return f'<Portfolio {self.name}>'

# Stock Model
class Stock:
    def __init__(self, portfolio_id, symbol, name, quantity, purchase_price, purchase_date, currency='USD', notes=None):
        self.portfolio_id = str(portfolio_id)  # Reference to the portfolio (as a string)
        self.symbol = symbol  # Stock symbol (e.g., AAPL, TSLA)
        self.name = name  # Full name of the stock
        self.quantity = quantity  # Number of shares
        self.purchase_price = purchase_price  # Price per share at purchase
        self.purchase_date = purchase_date  # Date when the stock was purchased
        self.currency = currency  # Currency of the purchase price
        self.notes = notes  # Optional notes about the stock

    def to_dict(self):
        if isinstance(self.purchase_date, date):
            self.purchase_date = datetime.combine(self.purchase_date, datetime.min.time())
        return {
            "portfolio_id": ObjectId(self.portfolio_id),
            "symbol": self.symbol,
            "name": self.name,
            "quantity": self.quantity,
            "purchase_price": self.purchase_price,
            "purchase_date": self.purchase_date,
            "currency": self.currency,
            "notes": self.notes
        }

    @staticmethod
    def from_dict(data):
        purchase_date = data["purchase_date"]
        if isinstance(purchase_date, datetime):
            purchase_date = purchase_date.date()
        return Stock(
            portfolio_id=str(data["portfolio_id"]),
            symbol=data["symbol"],
            name=data["name"],
            quantity=data["quantity"],
            purchase_price=data["purchase_price"],
            purchase_date=purchase_date,
            currency=data.get("currency", "USD"),
            notes=data.get("notes")
        )

    def __repr__(self):
        return f'<Stock {self.symbol} - {self.quantity} shares @ {self.purchase_price} {self.currency}>'
