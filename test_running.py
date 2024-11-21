from pymongo import MongoClient

# MongoDB Atlas connection string
uri = "mongodb+srv://arjuncrevathi:Arjun_1987@serverlessinstance0.ppr5qpz.mongodb.net/wealth_ledger"
client = MongoClient(uri)

# Select the database and collection
db = client["wealth_ledger"]
users_collection = db["users"]

# Delete the invalid document
result = users_collection.delete_one({"_id": None})
print(f"Deleted {result.deleted_count} invalid document(s).")