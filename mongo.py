import os
from pymongo import MongoClient

DBS = [
    os.getenv("DB1_URL"),
    os.getenv("DB2_URL"),
    os.getenv("DB3_URL"),
    os.getenv("DB4_URL")
]

DB_NAME = os.getenv("DATABASE_NAME")
COLL_NAME = os.getenv("COLLECTION_NAME")

clients = [
    MongoClient(url)[DB_NAME][COLL_NAME]
    for url in DBS if url
]
