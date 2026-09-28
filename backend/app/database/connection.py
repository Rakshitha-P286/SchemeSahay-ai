from pymongo import MongoClient
from app.config.settings import settings

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db]

def get_db():
    return db
