# Microservices FastAPI Demo

A demonstration of microservices architecture using FastAPI and Redis for inter-service communication.

## Overview

This project implements a simple e-commerce flow with two microservices:

- **Inventory Service** - Manages products (create, read, delete)
- **Payment Service** - Handles order creation and processing

Services communicate asynchronously via Redis Streams.

## Architecture

```
┌─────────────┐     ┌─────────────┐
│  Inventory  │     │   Payment   │
│  (port 8000)│     │ (port 8001) │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
           ┌─────┴─────┐
           │   Redis   │
           └───────────┘
```

**Flow:**
1. Client creates an order via Payment service
2. Payment service fetches product from Inventory service
3. Order is created with "pending" status
4. Background task marks order "completed" after 5 seconds
5. Inventory decreases product quantity via Redis Stream
6. On refund, quantity is restored

## Prerequisites

- Python 3.8+
- Redis (local or cloud instance)

## Quick Start

### 1. Install dependencies

```bash
# Inventory service
cd inventory
pip install -r requirements.txt

# Payment service
cd payment
pip install fastapi uvicorn redis-om python-dotenv requests
```

### 2. Configure Redis

Create a `.env` file in the root directory:

```env
HOST=your-redis-host
PORT=your-redis-port
PASSWORD=your-redis-password
```

### 3. Run the services

Start each component in separate terminals:

```bash
# Terminal 1 - Inventory API
cd inventory
uvicorn main:app --reload --port 8000

# Terminal 2 - Payment API
cd payment
uvicorn main:app --reload --port 8001

# Terminal 3 - Inventory Consumer
cd inventory
python consumer.py

# Terminal 4 - Payment Consumer
cd payment
python consumer.py
```

## API Endpoints

### Inventory Service (port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products |
| POST | `/products` | Create a product |
| GET | `/products/{pk}` | Get product by ID |
| DELETE | `/products/{pk}` | Delete a product |

### Payment Service (port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/{pk}` | Get order by ID |
| POST | `/orders` | Create a new order |

### Example: Create an Order

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{"id": "PRODUCT_ID", "quantity": 1}'
```

## Project Structure

```
.
├── inventory/
│   ├── main.py       # FastAPI app & product models
│   └── consumer.py   # Redis consumer for order events
├── payment/
│   ├── main.py       # FastAPI app & order models
│   └── consumer.py   # Redis consumer for refund events
└── .env              # Environment variables
```

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Redis](https://redis.io/) - In-memory data store
- [redis-om](https://redis.com/developers/redis-om-python/) - Redis object mapper for Python

## License

MIT