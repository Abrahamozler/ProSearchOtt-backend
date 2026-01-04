from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongo import clients
from parser import parse_title, parse_quality

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/movies")
def movies():
    result = {}

    for coll in clients:
        try:
            cursor = coll.find({}, {
                "file_name": 1,
                "file_ref": 1
            }).limit(300)

            for d in cursor:
                name = d.get("file_name")
                if not name:
                    continue

                title = parse_title(name)
                quality = parse_quality(name)

                if title not in result:
                    result[title] = {
                        "title": title,
                        "movie_id": title.replace(" ", "_").lower(),
                        "files": []
                    }

                result[title]["files"].append({
                    "quality": quality
                })

        except Exception as e:
            print("DB error:", e)

    return list(result.values())


@app.get("/search")
def search(q: str):
    result = {}

    for coll in clients:
        try:
            cursor = coll.find(
                {"file_name": {"$regex": q, "$options": "i"}},
                {"file_name": 1}
            ).limit(100)

            for d in cursor:
                name = d.get("file_name")
                title = parse_title(name)
                quality = parse_quality(name)

                if title not in result:
                    result[title] = {
                        "title": title,
                        "movie_id": title.replace(" ", "_").lower(),
                        "files": []
                    }

                result[title]["files"].append({
                    "quality": quality
                })

        except Exception as e:
            print("Search error:", e)

    return list(result.values())
