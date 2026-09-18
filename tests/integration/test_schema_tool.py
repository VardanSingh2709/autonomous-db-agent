import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.tools.schema_tool import inspect_schema


def test_inspect_schema_returns_all_expected_tables():
    result = inspect_schema()
    table_names = {row["table_name"] for row in result}
    expected_tables = {
        "regions", "product_categories", "products", "customers",
        "marketing_campaigns", "orders", "order_items", "subscriptions", "payments"
    }
    assert expected_tables.issubset(table_names)


def test_inspect_schema_returns_column_details():
    result = inspect_schema()
    customer_columns = [row for row in result if row["table_name"] == "customers"]
    column_names = {row["column_name"] for row in customer_columns}
    assert "id" in column_names
    assert "region_id" in column_names
    assert "is_returning" in column_names


def test_inspect_schema_result_is_json_safe():
    import json
    result = inspect_schema()
    # This will raise if any value isn't JSON-serializable (e.g. a raw Decimal or date)
    json.dumps(result)