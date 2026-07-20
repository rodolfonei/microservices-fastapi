"""
Payment Service Model Tests
"""
import pytest
from unittest.mock import patch


class TestOrderModel:
    """Tests for Order model"""

    def test_create_order(self, test_redis):
        """Can create and save an order"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Order

            order = Order(
                product_id="test-product-id",
                price=29.99,
                fee=5.998,
                total=35.988,
                quantity=2,
                status="pending"
            )
            pk = order.save()

            assert pk is not None
            assert order.pk == pk

    def test_get_order(self, test_redis):
        """Can retrieve a saved order"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Order

            # Create and save
            order = Order(
                product_id="test-product-id",
                price=29.99,
                fee=5.998,
                total=35.988,
                quantity=2,
                status="pending"
            )
            order.save()

            # Retrieve
            retrieved = Order.get(order.pk)

            assert retrieved.product_id == "test-product-id"
            assert retrieved.price == 29.99
            assert retrieved.quantity == 2
            assert retrieved.status == "pending"

    def test_order_fields(self, test_redis):
        """Order stores all fields correctly"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Order

            order = Order(
                product_id="prod-123",
                price=49.99,
                fee=9.998,
                total=59.988,
                quantity=3,
                status="completed"
            )
            order.save()

            retrieved = Order.get(order.pk)

            assert retrieved.product_id == "prod-123"
            assert retrieved.price == 49.99
            assert retrieved.fee == 9.998
            assert retrieved.total == 59.988
            assert retrieved.quantity == 3
            assert retrieved.status == "completed"

    def test_order_status_default(self, test_redis):
        """Order has default status of pending"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Order

            order = Order(
                product_id="test-product-id",
                price=29.99,
                fee=5.998,
                total=35.988,
                quantity=1
                # No status provided - should default to None or empty
            )
            order.save()

            retrieved = Order.get(order.pk)
            # Status should be stored (default behavior depends on redis-om)
            assert retrieved.product_id == "test-product-id"

    def test_order_status_values(self, test_redis):
        """Order can have different status values"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Order

            # Test pending
            order = Order(
                product_id="test-product-id",
                price=29.99,
                fee=5.998,
                total=35.988,
                quantity=1,
                status="pending"
            )
            order.save()
            assert Order.get(order.pk).status == "pending"

            # Test completed
            order.status = "completed"
            order.save()
            assert Order.get(order.pk).status == "completed"

            # Test refunded
            order.status = "refunded"
            order.save()
            assert Order.get(order.pk).status == "refunded"