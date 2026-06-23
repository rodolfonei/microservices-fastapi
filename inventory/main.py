import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from redis_om import get_redis_connection, HashModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

redis = get_redis_connection(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    password=os.getenv("PASSWORD"),
    decode_responses=True
)

class Product(HashModel, index=True):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/products")
def all():
    return Product.all_pks()

@app.post("/products")
def create(product: Product):
    return product.save()
