"""Tests for the low-stock inventory endpoint"""
import pytest


class TestLowStockEndpoint:
    """Test suite for /api/inventory/low-stock endpoint"""

    def test_get_low_stock_items(self, client):
        """Test getting all low-stock items."""
        response = client.get("/api/inventory/low-stock")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4  # Based on current test data

    def test_low_stock_threshold_validation(self, client):
        """Test that all returned items are actually low-stock."""
        response = client.get("/api/inventory/low-stock")
        data = response.json()

        # Verify all items meet the low-stock criteria
        for item in data:
            assert item["quantity_on_hand"] <= item["reorder_point"], \
                f"Item {item['sku']} does not meet low-stock criteria"

    def test_low_stock_calculated_fields(self, client):
        """Test that shortage fields are calculated correctly."""
        response = client.get("/api/inventory/low-stock")
        data = response.json()

        for item in data:
            assert "shortage" in item
            assert "shortage_percentage" in item

            # Verify shortage calculation
            expected_shortage = item["reorder_point"] - item["quantity_on_hand"]
            assert item["shortage"] == expected_shortage, \
                f"Item {item['sku']} has incorrect shortage calculation"

            # Verify percentage calculation
            if item["reorder_point"] > 0:
                expected_pct = round((expected_shortage / item["reorder_point"]) * 100, 1)
                assert item["shortage_percentage"] == expected_pct, \
                    f"Item {item['sku']} has incorrect shortage percentage"

    def test_low_stock_sorting(self, client):
        """Test that items are sorted by urgency (shortage percentage descending)."""
        response = client.get("/api/inventory/low-stock")
        data = response.json()

        # Verify descending order by shortage_percentage
        for i in range(len(data) - 1):
            assert data[i]["shortage_percentage"] >= data[i + 1]["shortage_percentage"], \
                "Items are not sorted by shortage percentage descending"

    def test_low_stock_filter_by_warehouse(self, client):
        """Test filtering low-stock items by warehouse."""
        response = client.get("/api/inventory/low-stock?warehouse=Tokyo")
        assert response.status_code == 200
        data = response.json()

        # Tokyo has 3 low-stock items based on current test data
        assert len(data) == 3

        # Verify all items are from Tokyo
        for item in data:
            assert item["warehouse"] == "Tokyo"
            assert item["quantity_on_hand"] <= item["reorder_point"]

    def test_low_stock_filter_by_category(self, client):
        """Test filtering low-stock items by category."""
        response = client.get("/api/inventory/low-stock?category=Actuators")
        assert response.status_code == 200
        data = response.json()

        # Verify all items are Actuators
        for item in data:
            assert item["category"] == "Actuators"
            assert item["quantity_on_hand"] <= item["reorder_point"]

    def test_low_stock_combined_filters(self, client):
        """Test combining multiple filters."""
        response = client.get("/api/inventory/low-stock?warehouse=Tokyo&category=Actuators")
        assert response.status_code == 200
        data = response.json()

        # Verify all items match both filters
        for item in data:
            assert item["warehouse"] == "Tokyo"
            assert item["category"] == "Actuators"
            assert item["quantity_on_hand"] <= item["reorder_point"]

    def test_low_stock_empty_result(self, client):
        """Test endpoint with filters that return no results."""
        # Use a warehouse that has no low-stock items
        response = client.get("/api/inventory/low-stock?warehouse=NonExistentWarehouse")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_low_stock_all_filter_value(self, client):
        """Test that 'all' filter value returns all low-stock items."""
        response = client.get("/api/inventory/low-stock?warehouse=all&category=all")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Same as unfiltered

    def test_low_stock_zero_reorder_point_edge_case(self, client):
        """Test handling of items with zero reorder point."""
        response = client.get("/api/inventory/low-stock")
        data = response.json()

        # Verify that items with reorder_point=0 don't cause division errors
        for item in data:
            if item["reorder_point"] == 0:
                assert item["shortage_percentage"] == 0

    def test_low_stock_response_structure(self, client):
        """Test that response includes all expected fields."""
        response = client.get("/api/inventory/low-stock")
        data = response.json()

        required_fields = [
            "id", "sku", "name", "category", "warehouse",
            "quantity_on_hand", "reorder_point", "unit_cost",
            "location", "last_updated", "shortage", "shortage_percentage"
        ]

        for item in data:
            for field in required_fields:
                assert field in item, f"Missing required field: {field}"
