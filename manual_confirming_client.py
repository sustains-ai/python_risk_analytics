from flask import current_app

# Assuming `mongo` is your MongoDB client and initialized
with current_app.app_context():
    mongo.db.users.update_one(
        {"email": "arjuncrevathi@gmail.com"},  # Filter to find the user
        {"$set": {"confirmed": True}}         # Update confirmed to true
    )
    print("User email confirmation updated successfully!")
