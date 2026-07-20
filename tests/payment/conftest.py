"""
Payment service test configuration
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add payment directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "payment"))


@pytest.fixture
def test_redis(clean_redis):
    """
    Provides a clean Redis instance for payment tests.
    """
    return clean_redis


@pytest.fixture
def mock_inventory_response():
    """
    Provides a mock response for inventory service HTTP calls.
    """
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "id": "test-product-id",
        "name": "Test Product",
        "price": 29.99,
        "quantity": 100
    }
    return mock_resp


@pytest.fixture
def client(test_redis, mock_inventory_response):
    """
    Provides a test client with properly configured test Redis.
    """
    # Clear main module to force re-import with patched Redis
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'main' or mod_name.startswith('main.'):
            del sys.modules[mod_name]

    # Patch both Redis connection AND requests.get BEFORE importing main
    with patch('main.get_redis_connection', return_value=test_redis):
        with patch('requests.get', return_value=mock_inventory_response):
            from main import app, Order

            # Patch Order's database connection
            Order.Meta.database = test_redis

            from fastapi.testclient import TestClient
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def sample_order_data():
    """
    Provides sample order data for tests.
    """
    return {
        "id": "test-product-id",
        "quantity": 2
    }


@pytest.fixture
def sample_product_data():
    """
    Provides sample product data for the mocked inventory response.
    """
    return {
        "id": "test-product-id",
        "name": "Test Product",
        "price": 29.99,
        "quantity": 100
    }