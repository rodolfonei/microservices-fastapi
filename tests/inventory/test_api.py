"""
Inventory Service API Tests
"""
import pytest


class TestGetProducts:
    """Tests for GET /products endpoint"""

    def test_get_all_products_empty(self, client):
        """Returns empty list when no products exist"""
        response = client.get("/products")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_products_with_data(self, client, sample_product_data):
        """Returns list of products when products exist"""
        # Create a product first
        client.post("/products", json=sample_product_data)

        response = client.get("/products")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_product_data["name"]


class TestCreateProduct:
    """Tests for POST /products endpoint"""

    def test_create_product(self, client, sample_product_data):
        """Creates a new product and returns it"""
        response = client.post("/products", json=sample_product_data)

        assert response.status_code == 200
        data = response.json()
        assert "pk" in data  # redis-om adds primary key
        assert data["name"] == sample_product_data["name"]
        assert data["price"] == sample_product_data["price"]
        assert data["quantity"] == sample_product_data["quantity"]


class TestGetProduct:
    """Tests for GET /products/{pk} endpoint"""

    def test_get_product_not_found(self, client):
        """Returns 404 when product doesn't exist"""
        response = client.get("/products/nonexistent-id")

        assert response.status_code == 404

    def test_get_product(self, client, created_product):
        """Returns product by primary key"""
        pk = created_product["pk"]

        response = client.get(f"/products/{pk}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pk
        assert data["name"] == created_product["name"]


class TestDeleteProduct:
    """Tests for DELETE /products/{pk} endpoint"""

    def test_delete_product_not_found(self, client):
        """Returns 404 when product doesn't exist"""
        response = client.delete("/products/nonexistent-id")

        assert response.status_code == 404

    def test_delete_product(self, client, created_product):
        """Deletes a product successfully"""
        pk = created_product["pk"]

        response = client.delete(f"/products/{pk}")

        assert response.status_code == 200

        # Verify product is deleted
        get_response = client.get(f"/products/{pk}")
        assert get_response.status_code == 404