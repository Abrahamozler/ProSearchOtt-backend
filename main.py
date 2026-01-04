from fastapi import FastAPI, Query
from pymongo import MongoClient
import os

app = FastAPI()

# Mongo setup
client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("MONGO_DB", "cluster0")]

# Load all collections (DB names don't matter)
COLLECTION_NAMES = [
    os.getenv("DB1_NAME"),
    os.getenv("DB2_NAME"),
    os.getenv("DB3_NAME"),
    os.getenv("DB4_NAME"),
]

collections = [db[name] for name in COLLECTION_NAMES if name]

# -------- HELPERS --------
def merge_docs(docs):
    result = {}
    for doc in docs:
        mid = doc["movie_id"]
        result.setdefault(mid, {
            "movie_id": mid,
            "title": doc["title"],
            "poster": doc.get("poster"),
            "files": []
        })
        result[mid]["files"].append({
            "quality": doc["quality"]
        })
    return list(result.values())

# -------- API --------
@app.get("/movies")
def movies_list():
    docs = []
    for col in collections:
        docs.extend(list(col.find({}, {"_id": 0})))
    return merge_docs(docs)

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    docs = []
    for col in collections:
        docs.extend(list(col.find(
            {"title": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        )))
    return merge_docs(docs)
