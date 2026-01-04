from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongo import clients
from parser import parse_title, parse_quality
from tmdb import tmdb_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/movies")
def movies():
    result = {}

    for coll in clients:
        for d in coll.find().sort("_id", -1).limit(500):
            title = parse_title(d.get("file_name",""))
            q = parse_quality(d.get("file_name",""))

            if title not in result:
                result[title] = {
                    "title": title,
                    "movie_id": title.replace(" ", "_").lower(),
                    "files": [],
                    **tmdb_data(title)
                }

            result[title]["files"].append({
                "quality": q,
                "file_ref": d.get("file_ref")
            })

    return list(result.values())

@app.get("/search")
def search(q: str):
    result = {}

    for coll in clients:
        for d in coll.find({
            "$or":[
                {"file_name":{"$regex":q,"$options":"i"}},
                {"caption":{"$regex":q,"$options":"i"}}
            ]
        }).limit(100):

            title = parse_title(d.get("file_name",""))
            ql = parse_quality(d.get("file_name",""))

            if title not in result:
                result[title] = {
                    "title": title,
                    "movie_id": title.replace(" ", "_").lower(),
                    "files": [],
                    **tmdb_data(title)
                }

            result[title]["files"].append({
                "quality": ql,
                "file_ref": d.get("file_ref")
            })

    return list(result.values())
