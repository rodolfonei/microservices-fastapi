"""
Inventory service test configuration
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add inventory directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "inventory"))


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset cached modules before each test"""
    # Clear cached inventory modules
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'main' or mod_name.startswith(('main.', 'redis_om')):
            pass  # Don't remove yet, we'll handle specifically
    yield
    # Cleanup after test
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'main' or mod_name.startswith('main.'):
            del sys.modules[mod_name]


@pytest.fixture
def test_redis(clean_redis):
    """
    Provides a clean Redis instance for inventory tests.
    """
    return clean_redis


@pytest.fixture
def client(test_redis):
    """
    Provides a test client with properly configured test Redis.
    """
    # Clear main module to force re-import with patched Redis
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'main' or mod_name.startswith('main.'):
            del sys.modules[mod_name]

    # Patch get_redis_connection BEFORE importing main
    with patch('main.get_redis_connection', return_value=test_redis):
        from main import app, Product, redis

        # Also patch the Product model's database connection
        Product.Meta.database = test_redis

        from fastapi.testclient import TestClient
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def sample_product_data():
    """
    Provides sample product data for tests.
    """
    return {
        "name": "Test Product",
        "price": 29.99,
        "quantity": 100
    }


@pytest.fixture
def created_product(client, sample_product_data):
    """
    Creates a sample product and returns its data.
    """
    response = client.post("/products", json=sample_product_data)
    assert response.status_code == 200
    return response.json()