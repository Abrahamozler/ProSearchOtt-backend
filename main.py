from fastapi import FastAPI, Query
from pymongo import MongoClient
import os

app = FastAPI(title="MovieFlix Backend")

# ------------------ Mongo Setup ------------------

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Media")

DB1_NAME = os.getenv("DB1_NAME")  # Media1
DB2_NAME = os.getenv("DB2_NAME")  # Media2
DB3_NAME = os.getenv("DB3_NAME")  # Media3
DB4_NAME = os.getenv("DB4_NAME")  # Media4

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]

COLLECTION_NAMES = [DB1_NAME, DB2_NAME, DB3_NAME, DB4_NAME]
collections = [db[name] for name in COLLECTION_NAMES if name]

# ------------------ Helpers ------------------

def merge_movies(docs):
    """
    Merge same movie_id from all collections
    Return only available qualities
    """
    result = {}

    for doc in docs:
        movie_id = doc.get("movie_id")
        if not movie_id:
            continue

        result.setdefault(movie_id, {
            "movie_id": movie_id,
            "title": doc.get("title", "Unknown"),
            "poster": doc.get("poster"),
            "files": []
        })

        result[movie_id]["files"].append({
            "quality": doc.get("quality")
        })

    return list(result.values())

# ------------------ API Routes ------------------

@app.get("/")
def root():
    return {"status": "MovieFlix backend running"}

@app.get("/movies")
def get_movies():
    docs = []
    for col in collections:
        docs.extend(list(col.find({}, {"_id": 0})))
    return merge_movies(docs)

@app.get("/search")
def search_movies(q: str = Query(..., min_length=1)):
    docs = []
    for col in collections:
        docs.extend(list(col.find(
            {"title": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        )))
    return merge_movies(docs)
