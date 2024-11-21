from pymongo import MongoClient

# Replace with your MongoDB Atlas connection string
uri = "mongodb+srv://arjuncrevathi:Arjun_1987@serverlessinstance0.ppr5qpz.mongodb.net/wealth_ledger"
client = MongoClient(uri)

# Select the database and collection
db = client["wealth_ledger"]
users_collection = db["users"]

# Fetch and print all user documents
users = list(users_collection.find())
if users:
    print("Users in the database:")
    for user in users:
        print(user)
else:
    print("No users found in the database.")
