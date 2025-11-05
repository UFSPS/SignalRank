# database/db.py
# MongoDB connection and schema setup for SignalRank
# Only need to run once when first setting up the database

from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

try:
    client.admin.command('ping')
    print(f"Connected: {MONGO_DB_NAME}")
except Exception as e:
    print("Failed:")
    print(e)
    exit()

# Define collection schemas
schemas = {
    "users": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["discord_id", "points"],
            "properties": {
                "discord_id": {"bsonType": "string"},
                "points": {"bsonType": "int"},
                "level": {"bsonType": "int"},
                "metadata": {
                    "bsonType": "object",
                    "properties": {
                        "last_msg": {"bsonType": "string"},
                        "recorded_msgs": {"bsonType": "int"}
                    }
                }
            }
        }
    },
    "transactions": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "delta_points", "reason", "timestamp"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "delta_points": {"bsonType": "int"},
                "reason": {"bsonType": "string"},
                "timestamp": {"bsonType": "date"}
            }
        }
    },
    "activities": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["type", "content", "timestamp"],
            "properties": {
                "type": {"bsonType": "string"},
                "content": {"bsonType": "string"},
                "timestamp": {"bsonType": "date"}
            }
        }
    }
}

def setup_collections():
    existing = db.list_collection_names()

    for col, schema in schemas.items():
        if col not in existing:
            db.create_collection(col)
            print(f"Created collection: {col}")
        else:
            print(f"Collection exists: {col}")

        db.command("collMod", col, validator=schema, validationLevel="moderate")

def seed_data():
    if db.users.count_documents({}) == 0:
        db.users.insert_one({
            "discord_id": "1234567890",
            "points": 100,
            "level": 1,
            "metadata": {
                "last_msg": datetime.utcnow().isoformat(),
                "recorded_msgs": 1
            }
        })

    if db.transactions.count_documents({}) == 0:
        db.transactions.insert_one({
            "user_id": "1234567890",
            "delta_points": 50,
            "reason": "Initial setup",
            "timestamp": datetime.utcnow()
        })

    if db.activities.count_documents({}) == 0:
        db.activities.insert_one({
            "type": "setup_test",
            "content": "Initial activity entry",
            "timestamp": datetime.utcnow()
        })

if __name__ == "__main__":
    setup_collections()
    seed_data()
