# Test Strategy Plan for Microservices FastAPI Project

## Overview
Set up automated unit and integration tests for both Inventory and Payment services using pytest with fakeredis for isolated testing.

---

## Project Structure (Implemented)

```
tests/
├── __init__.py
├── conftest.py                    # Root fixtures (fakeredis)
├── inventory/
│   ├── __init__.py
│   ├── conftest.py               # Service fixtures with Redis mocking
│   ├── test_models.py            # Unit tests for Product model
│   └── test_api.py               # API tests for Product endpoints
├── payment/
│   ├── __init__.py
│   ├── conftest.py               # Service fixtures with Redis + HTTP mocking
│   ├── test_models.py            # Unit tests for Order model
│   └── test_api.py               # API tests for Order endpoints
└── integration/
    └── (to be implemented)
```

---

## Dependencies Added

In both `inventory/requirements.txt` and `payment/requirements.txt`:
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
fakeredis>=2.19.0
testcontainers>=3.7.0
```

---

## Implementation Status

### ✅ Step 1: Test Infrastructure

**`tests/conftest.py`** - Root fixtures
- `redis_server` fixture: fakeredis server (session scope)
- `clean_redis` fixture: clean Redis for each test (function scope)

**`tests/inventory/conftest.py`** - Inventory fixtures
- `test_redis`: clean Redis for inventory tests
- `client`: FastAPI TestClient with patched Redis
- `sample_product_data`: sample product dict
- `created_product`: creates a product via API

**`tests/payment/conftest.py`** - Payment fixtures
- `test_redis`: clean Redis for payment tests
- `mock_inventory_response`: Mock HTTP response for inventory calls
- `client`: TestClient with Redis + requests.get mocked
- `sample_order_data`: sample order dict

### ✅ Step 2: Inventory Service Tests

**`tests/inventory/test_models.py`** (4 tests)
- `test_create_product`: create and save Product
- `test_get_product`: retrieve saved Product
- `test_delete_product`: delete Product
- `test_product_fields`: verify all fields stored correctly

**`tests/inventory/test_api.py`** (7 tests)
- `test_get_all_products_empty`: empty list when no products
- `test_get_all_products_with_data`: returns products when exist
- `test_create_product`: POST /products creates product
- `test_get_product_not_found`: 404 for non-existent product
- `test_get_product`: GET /products/{pk} returns product
- `test_delete_product_not_found`: 404 for non-existent product
- `test_delete_product`: DELETE /products/{pk} removes product

### ✅ Step 3: Payment Service Tests

**`tests/payment/test_models.py`** (5 tests)
- `test_create_order`: create and save Order
- `test_get_order`: retrieve saved Order
- `test_order_fields`: verify all fields stored correctly
- `test_order_status_default`: default status behavior
- `test_order_status_values`: pending/completed/refunded statuses

**`tests/payment/test_api.py`** (6 tests)
- `test_get_order_not_found`: 404 for non-existent order
- `test_create_order`: POST /orders creates order
- `test_create_order_calculates_totals`: verifies price/fee/total calculation
- `test_order_pending_status`: order starts as pending
- `test_order_completed_status_after_delay`: background task completes order
- `test_order_completed_status_mocked`: mocked version for fast tests

### ✅ Step 4: Error Handling Added

**`inventory/main.py`** - Added exception handlers:
- `NotFoundError` → 404 response
- Generic `Exception` → 500 response

**`payment/main.py`** - Added exception handlers:
- `NotFoundError` → 404 response
- Generic `Exception` → 500 response

---

## What's Left to Do

### Integration Tests (tests/integration/)

- `test_order_completed_triggers_inventory_decrease`:
  1. Create product in inventory (quantity: 10)
  2. Create order in payment (quantity: 2)
  3. Add to `order_completed` stream (simulate background task)
  4. Run inventory consumer logic
  5. Verify product quantity decreased to 8

- `test_refund_flow_when_product_not_found`:
  1. Create order with non-existent product_id
  2. Run payment consumer logic
  3. Verify message in `refund_order` stream
  4. Run inventory consumer logic
  5. Verify order status changed to "refunded"

### CI Configuration (Optional)

**`.github/workflows/test.yml`**
```yaml
- Run inventory tests
- Run payment tests
```

---

## Key Design Decisions

1. **fakeredis**: Used instead of Docker for simplicity - fast, no external dependencies, sufficient for most tests. Redis Streams behavior is mocked.

2. **TestClient from FastAPI**: `from starlette.testclient import TestClient` for HTTP testing - no need to run actual servers.

3. **Mock external HTTP calls**: In payment tests, mock `requests.get` to inventory service to avoid dependency on running inventory service.

4. **Module reloading in fixtures**: Clear `sys.modules` before importing to ensure fresh Redis connection in each test.

5. **Exception handlers**: Added to both services to return proper 404/500 HTTP responses instead of unhandled exceptions.

---

## Fixtures Implemented

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `redis_server` | session | fakeredis server |
| `clean_redis` | function | Clean Redis per test |
| `test_redis` | function | Service-specific Redis |
| `client` | function | FastAPI TestClient |
| `sample_product_data` | function | Product test data |
| `sample_order_data` | function | Order test data |
| `mock_inventory_response` | function | Mock HTTP response |
| `created_product` | function | Created product via API |

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/inventory/test_models.py tests/payment/test_models.py -v

# Inventory tests only
python -m pytest tests/inventory/ -v

# Payment tests only
python -m pytest tests/payment/ -v

# Integration tests (when implemented)
python -m pytest tests/integration/ -v

# With coverage
python -m pytest tests/ --cov=inventory --cov=payment --cov-report=html
```

---

## Success Criteria

- [x] Test infrastructure set up with fakeredis
- [x] API endpoints have basic happy-path tests
- [x] Models have CRUD operation tests
- [ ] Stream communication flow tested (integration tests pending)
- [x] Tests can run independently (no manual service startup)
- [x] Clear separation between unit and integration tests
- [ ] At least 80% code coverage on business logic (pending verification)