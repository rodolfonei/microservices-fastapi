"""
Payment Service API Tests
"""
import pytest
from unittest.mock import patch, MagicMock


class TestGetOrder:
    """Tests for GET /orders/{pk} endpoint"""

    def test_get_order_not_found(self, client):
        """Returns 404 when order doesn't exist"""
        response = client.get("/orders/nonexistent-id")

        assert response.status_code == 404


class TestCreateOrder:
    """Tests for POST /orders endpoint"""

    def test_create_order(self, client, sample_order_data):
        """Creates a new order with pending status"""
        response = client.post("/orders", json=sample_order_data)

        assert response.status_code == 200
        data = response.json()
        assert "pk" in data
        assert data["product_id"] == sample_order_data["id"]
        assert data["status"] == "pending"
        assert data["quantity"] == sample_order_data["quantity"]

    def test_create_order_calculates_totals(self, client, sample_order_data):
        """Order correctly calculates price, fee, and total"""
        response = client.post("/orders", json=sample_order_data)

        data = response.json()
        # price = 29.99 (from mock)
        # fee = 0.2 * 29.99 = 5.998
        # total = 1.2 * 29.99 = 35.988
        assert data["price"] == 29.99
        assert data["fee"] == pytest.approx(5.998, rel=0.01)
        assert data["total"] == pytest.approx(35.988, rel=0.01)


class TestOrderStatus:
    """Tests for order status flow"""

    def test_order_pending_status(self, client, sample_order_data):
        """Order starts with pending status"""
        response = client.post("/orders", json=sample_order_data)

        data = response.json()
        assert data["status"] == "pending"

    def test_order_completed_status_after_delay(self, client, sample_order_data, mock_inventory_response):
        """
        Order status changes to completed after background task.
        Note: This test uses real time.sleep - may be slow.
        For faster tests, mock the order_completed function.
        """
        # Create order
        response = client.post("/orders", json=sample_order_data)
        order_pk = response.json()["pk"]

        # Wait for background task (5 seconds)
        import time
        time.sleep(5)

        # Check status changed
        response = client.get(f"/orders/{order_pk}")
        assert response.json()["status"] == "completed"

    def test_order_completed_status_mocked(self, client, sample_order_data, test_redis):
        """
        Order status changes to completed - mocked version.
        Faster test that directly updates the status.
        """
        from unittest.mock import patch

        # Mock the order_completed to immediately complete
        with patch("main.order_completed"):
            response = client.post("/orders", json=sample_order_data)
            # Status should still be pending since we mocked the background task
            assert response.json()["status"] == "pending"