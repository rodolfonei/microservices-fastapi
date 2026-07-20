"""
Inventory Service Model Tests
"""
import pytest
from unittest.mock import patch, MagicMock


class TestProductModel:
    """Tests for Product model"""

    def test_create_product(self, test_redis):
        """Can create and save a product"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Product

            product = Product(
                name="Test Product",
                price=29.99,
                quantity=50
            )
            pk = product.save()

            assert pk is not None
            assert product.pk is not None

    def test_get_product(self, test_redis):
        """Can retrieve a saved product"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Product

            # Create and save
            product = Product(
                name="Test Product",
                price=29.99,
                quantity=50
            )
            product.save()

            # Retrieve
            retrieved = Product.get(product.pk)

            assert retrieved.name == "Test Product"
            assert retrieved.price == 29.99
            assert retrieved.quantity == 50

    def test_delete_product(self, test_redis):
        """Can delete a product"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Product

            # Create and save
            product = Product(
                name="Test Product",
                price=29.99,
                quantity=50
            )
            pk = product.save()

            # Delete
            Product.delete(pk)

            # Verify deletion
            from redis_om.model.model import NotFoundError
            with pytest.raises(NotFoundError):
                Product.get(pk)

    def test_product_fields(self, test_redis):
        """Product stores all fields correctly"""
        with patch("main.get_redis_connection", return_value=test_redis):
            from main import Product

            product = Product(
                name="Widget",
                price=19.99,
                quantity=25
            )
            product.save()

            retrieved = Product.get(product.pk)

            assert retrieved.name == "Widget"
            assert retrieved.price == 19.99
            assert retrieved.quantity == 25