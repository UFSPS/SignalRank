from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

for col_name in ["users", "transactions", "activities"]:
    info = db.command("listCollections", filter={"name": col_name})
    validator = info["cursor"]["firstBatch"][0].get("options", {}).get("validator")
    print(f"{col_name} validator:")
    print(validator, "\n")
