from flask import Flask
from create_app import mongo, create_app

def clear_user_data():
    # Ensure the Flask app context is active
    app = create_app()
    with app.app_context():
        # Clear the 'users' collection
        user_result = mongo.db.users.delete_many({})
        print(f"Deleted {user_result.deleted_count} users from the database.")

        # Clear the 'finance_data' collection
        finance_result = mongo.db.finance_data.delete_many({})
        print(f"Deleted {finance_result.deleted_count} financial records from the database.")

if __name__ == "__main__":
    clear_user_data()
