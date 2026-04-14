import pymongo
import json
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "social_media_db"
COLLECTION_NAME = "posts"

def get_db():
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    return client[DB_NAME]

def insert_dummy_data():
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    # Clear existing
    collection.delete_many({})
    
    # Load from json
    with open("dummy_data.json", "r") as f:
        posts = json.load(f)
        
    # Convert created_at strings to proper datetime objects for MongoDB
    for post in posts:
        if isinstance(post.get("created_at"), str):
            post["created_at"] = datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        
    if posts:
        collection.insert_many(posts)
        print(f"Successfully inserted {len(posts)} dummy posts into MongoDB.")
    
if __name__ == "__main__":
    insert_dummy_data()
