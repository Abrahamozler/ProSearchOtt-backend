import os
from pymongo import MongoClient

DB_NAME = os.getenv("DATABASE_NAME")
COLL_NAME = os.getenv("COLLECTION_NAME")

if not DB_NAME or not COLL_NAME:
    raise RuntimeError(
        "DATABASE_NAME or COLLECTION_NAME env var missing"
    )

clients = []

for i in range(1, 5):
    url = os.getenv(f"DB{i}_URL")
    if url:
        client = MongoClient(url, serverSelectionTimeoutMS=5000)
        clients.append(client[DB_NAME][COLL_NAME])

if not clients:
    raise RuntimeError("No MongoDB URLs provided")
