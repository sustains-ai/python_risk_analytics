from create_app import mongo

def confirm_user(email):
    result = mongo.db.users.update_one(
        {"email": email},
        {"$set": {"confirmed": True}}
    )
    if result.modified_count > 0:
        print(f"Email {email} confirmed successfully.")
    else:
        print(f"No user found with email: {email}")

if __name__ == "__main__":
    confirm_user("your-email@example.com")  # Replace with the actual email you want to confirm.
