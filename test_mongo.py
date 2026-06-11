from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

print(client.server_info()["version"])