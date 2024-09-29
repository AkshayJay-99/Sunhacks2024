# database.py
# from pymongo import MongoClient
# from bson import ObjectId

# MONGODB_URL = "mongodb+srv://Akshay:FirstDB2024@akshay-cluster.63skn.mongodb.net/"
# client = MongoClient(MONGODB_URL)
# db = client["authDB"]  # Name your database
# users_collection = db["authDB"]

# # Utility to handle ObjectId in MongoDB
# def serialize_dict(d):
#     return {str(k): str(v) if isinstance(v, ObjectId) else v for k, v in d.items()}
