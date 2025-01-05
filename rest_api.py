from datetime import datetime, timezone
from bson import ObjectId
from flask import request, make_response, url_for, current_app
from flask_mail import Message
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash
from create_app import create_app, mongo, s, mail
from flask_cors import CORS

app = create_app()
api = Api(app)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

def send_confirmation_email(user_email):
    # Generate a confirmation token
    token = s.dumps(user_email, salt='email-confirm')  # Create a token with a salt
    msg = Message('Confirm Your Email', recipients=[user_email])  # Create the email message
    link = url_for('main.confirm_email', token=token, _external=True)  # Generate the confirmation URL

    # Email content
    msg.body = f'Please confirm your email address by clicking on the following link: {link}'
    try:
        # Send the email using Flask-Mail (SES)
        mail.send(msg)
        current_app.logger.info(f"Confirmation email sent to {user_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to send confirmation email: {str(e)}")


def to_string(_object):
    _object["id"] = _object["_id"]
    del _object["_id"]

    for key in _object:
        _object[key] = str(_object[key])

    return _object

class Register(Resource):
    def post(self):
        name = request.json["name"]
        email = request.json["email"]
        password = request.json["password"]

        if not all([name, email, password]):
            response = {
                "success": False,
                "message": "email, password and name are required."
            }
            return make_response(response, 400)

        existing_user = mongo.db.users.find_one({"email": email})

        if existing_user:
            response = {
                "success": False,
                "message": "Email already registered. Please log in or use a different email."
            }
            return make_response(response, 400)

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "default_currency": "AED",
            "confirmed": False  # Add a "confirmed" field to track email confirmation status
        }

        mongo.db.users.insert_one(new_user)

        # Send the confirmation email
        send_confirmation_email(email)

        response = {
            "success": True,
            "message": "A verification link has been sent to your email id"
        }

        return make_response(response, 200)


class Login(Resource):
    def post(self):
        email = request.json["email"]
        password = request.json["password"]

        print("Harsga", request.json)

        if not email or not password:
            response = {
                "success": False,
                "message": "email and password are required."
            }
            return make_response(response, 400)

        user_data = mongo.db.users.find_one({"email": email})

        if not user_data:
            response = {
                "success": False,
                "message": "Invalid email or password"
            }
            return make_response(response, 404)

        if not check_password_hash(user_data["password"], password):
            response = {
                "success": False,
                "message": "Invalid email or password"
            }
            return make_response(response, 404)

        if not user_data.get('confirmed', False):
            response = {
                "success": False,
                "message": "Please confirm your email address first"
            }
            return make_response(response, 400)

        response = {
            "success": True,
            "id": str(user_data["_id"])
        }

        return make_response(response, 200)

class User(Resource):
    def get(self, _id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(_id)})
        if not user_data:
            response = {
                "success": False,
                "message": "User not found"
            }
            return make_response(response, 404)

        response = {
            "id": str(user_data["_id"]),
            "name": user_data["name"],
            "email": user_data["email"]
        }

        return make_response(response, 200)


class Portfolio(Resource):
    def get(self, _id):
        portfolios = list(mongo.db.portfolios.find({"user_id": _id}))

        return list(map(to_string, portfolios))

    def post(self, _id):

        name = request.json["name"]
        description = request.json["description"]

        if not name or not description:
            response = {
                "success": False,
                "message": "name and description are required."
            }
            return make_response(response, 400)

        new_portfolio = {
            "user_id": _id,
            "name": name,
            "description": description,
            "created_at": str(datetime.now(timezone.utc))
        }

        mongo.db.portfolios.insert_one(new_portfolio)

        response = {"success": True}

        return make_response(response, 200)

    def put(self, _id):
        portfolio_id = ObjectId(_id)
        portfolio = mongo.db.portfolios.find_one({"_id": portfolio_id})
        if not portfolio:
            response = {"success": False, "message": "Record not found"}
            return make_response(response, 404)

        new_values = {"$set": request.json}

        mongo.db.portfolios.update_one({"_id": portfolio_id}, new_values)

        response = {"success": True}

        return make_response(response, 200)

    def delete(self, _id):
        portfolio_id = ObjectId(_id)
        portfolio = mongo.db.portfolios.find_one({"_id": portfolio_id})
        if not portfolio:
            response = {"success": False, "message": "Record not found"}
            return make_response(response, 404)

        mongo.db.portfolios.delete_one({"_id": portfolio_id})
        mongo.db.stocks.delete_many({"portfolio_id": portfolio_id})

        response = {"success": True}

        return make_response(response, 200)


class Stock(Resource):
    def get(self, _id):
        stocks = list(mongo.db.stocks.find({"portfolio_id": _id}))

        return list(map(to_string, stocks))

    def post(self, _id):
        name = request.json["name"]
        symbol = request.json["symbol"]
        quantity = request.json["quantity"]
        purchase_price = request.json["purchase_price"]
        purchase_date = request.json["purchase_date"]
        currency = request.json["currency"]
        notes = request.json["notes"]

        if not all([name, symbol, quantity, purchase_price, purchase_date, currency]):
            response = {
                "success": False,
                "message": "missing parameters"
            }

            return make_response(response, 400)

        new_stock = {
            "portfolio_id": _id,
            "symbol": symbol,
            "name": name,
            "quantity": quantity,
            "purchase_price": purchase_price,
            "purchase_date": purchase_date,
            "currency": currency,
            "notes": notes
        }

        mongo.db.stocks.insert_one(new_stock)
        response = {"success": True}

        return make_response(response, 200)

    def put(self, _id):
        stock_id = ObjectId(_id)
        print(stock_id)
        stock = mongo.db.stocks.find_one({"_id": stock_id})
        if not stock:
            response = {"success": False, "message": "Record not found"}
            return make_response(response, 404)

        new_values = {"$set": request.json}

        mongo.db.stocks.update_one({"_id": stock_id}, new_values)

        response = {"success": True}

        return make_response(response, 200)

    def delete(self, _id):
        stock_id = ObjectId(_id)
        stock = mongo.db.stocks.find_one({"_id": stock_id})
        if not stock:
            response = {"success": False, "message": "Record not found"}
            return make_response(response, 404)

        mongo.db.stocks.delete_one({"_id": stock_id})

        response = {"success": True}

        return make_response(response, 200)


api.add_resource(Register, "/oauth/register")
api.add_resource(Login, "/oauth/login")
api.add_resource(User, "/api/users/<string:_id>")
api.add_resource(Portfolio, "/api/portfolios/<string:_id>")
api.add_resource(Stock, "/api/stocks/<string:_id>")

if __name__ == "__main__":
    app.run(debug=True)
