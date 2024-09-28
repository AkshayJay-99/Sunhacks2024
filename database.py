# database.py
from pymongo import MongoClient
from bson import ObjectId

MONGODB_URL = "mongodb://localhost:27017"
client = MongoClient(MONGODB_URL)
db = client["auth_db"]  # Name your database

# Utility to handle ObjectId in MongoDB
def serialize_dict(d):
    return {str(k): str(v) if isinstance(v, ObjectId) else v for k, v in d.items()}
