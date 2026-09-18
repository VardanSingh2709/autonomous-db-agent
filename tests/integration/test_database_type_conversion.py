import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
from app.database.connection import run_query


def test_decimal_columns_convert_to_json_safe_floats():
    """Regression test for the Decimal-not-JSON-serializable bug from Phase 7."""
    result = run_query("SELECT price FROM products LIMIT 1;")
    assert isinstance(result[0]["price"], float)
    json.dumps(result)  # would raise if still a Decimal


def test_date_columns_convert_to_json_safe_strings():
    """Regression test for the date-not-JSON-serializable bug from Phase 7."""
    result = run_query("SELECT order_date FROM orders LIMIT 1;")
    assert isinstance(result[0]["order_date"], str)
    json.dumps(result)


def test_run_query_with_parameters_prevents_injection_style_input():
    """A malicious-looking string value should be treated as literal data, not SQL."""
    malicious_input = "North'; DROP TABLE regions; --"
    result = run_query("SELECT * FROM regions WHERE name = :region", {"region": malicious_input})
    assert result == []  # no matching region — the string was NOT executed as SQL

    # Confirm the table still exists and has data (i.e. nothing was actually dropped)
    still_there = run_query("SELECT COUNT(*) AS count FROM regions;")
    assert still_there[0]["count"] > 0