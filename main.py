from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "root working"}

@app.get("/movies")
def movies():
    return {
        "test": "movies route working",
        "ok": True
    }
