from fastapi import FastAPI, Query
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import os, re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_NAME = "Media"
COLLECTION_NAME = "Cluster0"

collections = []

for key in ["DB1_URL", "DB2_URL", "DB3_URL", "DB4_URL"]:
    url = os.getenv(key)
    if url:
        client = MongoClient(url)
        collections.append(client[DATABASE_NAME][COLLECTION_NAME])

def parse_text(text: str):
    if not text:
        return None, None, None

    # Quality
    q = re.search(r"(2160p|1080p|720p|480p)", text, re.I)
    quality = q.group(1).lower() if q else "unknown"

    # Episode
    e = re.search(r"(S\d{2}E\d{2})", text, re.I)
    episode = e.group(1).upper() if e else ""

    # Title cleanup
    title = re.sub(r"<.*?>|@\w+|S\d{2}E\d{2}|2160p|1080p|720p|480p|x264|x265|WEB.*", "", text, flags=re.I)
    title = title.replace(".", " ").replace("_", " ").strip()

    movie_id = f"{title}_{episode}".lower().replace(" ", "_")

    return movie_id, title, quality

def merge_movies(docs):
    result = {}

    for doc in docs:
        source_text = doc.get("file_name") or doc.get("caption")
        movie_id, title, quality = parse_text(source_text)

        if not movie_id:
            continue

        result.setdefault(movie_id, {
            "movie_id": movie_id,
            "title": title,
            "poster": None,
            "files": []
        })

        if quality not in [f["quality"] for f in result[movie_id]["files"]]:
            result[movie_id]["files"].append({"quality": quality})

    return list(result.values())

@app.get("/")
def root():
    return {"status": "Backend running (file_name + caption parse)"}

@app.get("/movies")
def movies():
    docs = []
    for col in collections:
        docs.extend(list(col.find({}, {"_id": 0})))
    return merge_movies(docs)

@app.get("/search")
def search(q: str = Query(...)):
    docs = []
    for col in collections:
        docs.extend(list(col.find(
            {"$or": [
                {"file_name": {"$regex": q, "$options": "i"}},
                {"caption": {"$regex": q, "$options": "i"}}
            ]},
            {"_id": 0}
        )))
    return merge_movies(docs)

@app.get("/movies")
def movies():
    docs = []
    for col in collections:
        docs.extend(list(col.find({}, {"_id": 0})))
    return merge_movies(docs)
