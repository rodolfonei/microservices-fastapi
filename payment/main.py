import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request 
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# TO DO: change to a different DB
redis = get_redis_connection(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    password=os.getenv("PASSWORD"),
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database: redis

