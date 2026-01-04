from fastapi import FastAPI, Query
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import os
import re

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Mongo Config --------------------
DATABASE_NAME = "Media"
COLLECTION_NAME = "Cluster0"

_collections = None

def get_collections():
    """
    Create Mongo connections lazily (ONLY ONCE).
    Prevents Koyeb worker crash.
    """
    global _collections
    if _collections is not None:
        return _collections

    _collections = []
    for key in ["DB1_URL", "DB2_URL", "DB3_URL", "DB4_URL"]:
        url = os.getenv(key)
        if not url:
            continue

        client = MongoClient(
            url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=5
        )
        _collections.append(client[DATABASE_NAME][COLLECTION_NAME])

    return _collections

# -------------------- Helpers --------------------
def parse_text(text: str):
    if not text:
        return None, None, None

    # Quality
    q = re.search(r"(2160p|1080p|720p|480p)", text, re.I)
    quality = q.group(1) if q else "unknown"

    # Episode
    e = re.search(r"(S\d{2}E\d{2})", text, re.I)
    episode = e.group(1).upper() if e else ""

    # Title cleanup
    title = re.sub(
        r"<.*?>|@\w+|S\d{2}E\d{2}|2160p|1080p|720p|480p|x264|x265|WEB.*",
        "",
        text,
        flags=re.I
    )
    title = title.replace(".", " ").replace("_", " ").strip()

    movie_id = f"{title}_{episode}".lower().replace(" ", "_") if title else None
    return movie_id, title, quality


def merge_movies(docs):
    result = {}

    for doc in docs:
        source = doc.get("file_name") or doc.get("caption")
        movie_id, title, quality = parse_text(source)

        # Never skip a document
        if not movie_id:
            movie_id = "unknown_" + str(abs(hash(source)))
            title = title or "Unknown"

        result.setdefault(movie_id, {
            "movie_id": movie_id,
            "title": title,
            "poster": None,
            "files": []
        })

        if quality not in [f["quality"] for f in result[movie_id]["files"]]:
            result[movie_id]["files"].append({"quality": quality})

    return list(result.values())

# -------------------- Routes --------------------
@app.get("/")
def root():
    return {"status": "Backend running (stable, mongo enabled)"}

@app.get("/movies")
def movies():
    docs = []
    for col in get_collections():
        docs.extend(
            list(col.find({}, {"_id": 0}).limit(200))
        )
    return merge_movies(docs)

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    docs = []
    for col in get_collections():
        docs.extend(
            list(
                col.find(
                    {
                        "$or": [
                            {"file_name": {"$regex": q, "$options": "i"}},
                            {"caption": {"$regex": q, "$options": "i"}}
                        ]
                    },
                    {"_id": 0}
                ).limit(200)
            )
        )
    return merge_movies(docs)
