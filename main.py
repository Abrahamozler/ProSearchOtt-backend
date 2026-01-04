from fastapi import FastAPI, Query
from pymongo import MongoClient
import os

app = FastAPI()
client = MongoClient(os.getenv("MONGO_URL"))
db = client["cluster0"]
movies = db["movies"]

@app.get("/movies")
def movies_list():
    return list(movies.find({}, {"_id": 0}))

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    return list(movies.find({"title": {"$regex": q, "$options": "i"}}, {"_id": 0}))
