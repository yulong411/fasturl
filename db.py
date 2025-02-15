from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client[str(Config.DB_NAME)]