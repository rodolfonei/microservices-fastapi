# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI microservices demo with two services communicating via Redis Streams.

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

## Running the Services

Each service requires its own terminal:

```bash
# Inventory service (port 8000)
cd inventory
uvicorn main:app --reload --port 8000

# Payment service (port 8001)
cd payment
uvicorn main:app --reload --port 8001

# Background consumers (separate terminals)
cd inventory
python consumer.py

cd payment
python consumer.py
```

## Architecture

- **Inventory Service** (`inventory/main.py`): Manages products (CRUD). Runs on port 8000.
- **Payment Service** (`payment/main.py`): Handles orders. Calls inventory service via HTTP, creates orders in Redis. Runs on port 8001.
- **Redis Streams**: Used for async communication between services.
  - `order_completed` stream: Payment → Inventory (triggers inventory decrease)
  - `refund_order` stream: Inventory → Payment (triggers refund)

## Redis Connection

Both services use Redis via `redis-om`. Connection is configured in `.env`:
- `HOST`, `PORT`, `PASSWORD` - Redis Cloud credentials

## Key Patterns

1. **Order creation flow** (`payment/main.py:43-62`):
   - Receive order request → fetch product from inventory → create order with "pending" status → background task marks "completed" after 5s → publishes to `order_completed` stream

2. **Consumer pattern** (`inventory/consumer.py`, `payment/consumer.py`):
   - Uses Redis Stream consumer groups (`xgroup_create`, `xreadgroup`)
   - Infinite loop with 1s sleep polling

3. **Inventory decrease** (`payment/consumer.py:18-23`):
   - Listens to `order_completed` → decreases product quantity → if product not found, pushes to `refund_order`

4. **Refund handling** (`inventory/consumer.py:18-21`):
   - Listens to `refund_order` → updates order status to "refunded"