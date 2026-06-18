from fastapi import FastAPI
from dotenv import load_dotenv
from redis_om import get_redis_connection, HashModel

load_dotenv()

app = FastAPI()

redis = get_redis_connection(
    host=os.getenv("HOST"),
    port=os.getenv("PORT")
    password=os.getenv("PASSWORD")
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

