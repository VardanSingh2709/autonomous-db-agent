import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.tools.sql_tool import execute_readonly_sql


def test_rejects_drop_table():
    result = execute_readonly_sql("DROP TABLE orders;")
    assert "error" in result
    assert "forbidden" in result["error"].lower() or "only select" in result["error"].lower()


def test_rejects_delete():
    result = execute_readonly_sql("DELETE FROM customers WHERE id = 1;")
    assert "error" in result


def test_rejects_update():
    result = execute_readonly_sql("UPDATE customers SET name = 'hacked' WHERE id = 1;")
    assert "error" in result


def test_rejects_query_not_starting_with_select_or_with():
    result = execute_readonly_sql("EXPLAIN SELECT * FROM customers;")
    assert "error" in result


def test_allows_plain_select():
    result = execute_readonly_sql("SELECT COUNT(*) FROM regions;")
    assert isinstance(result, list)
    assert "error" not in (result[0] if result else {})


def test_allows_cte_with_with_clause():
    result = execute_readonly_sql("WITH r AS (SELECT * FROM regions) SELECT COUNT(*) FROM r;")
    assert isinstance(result, list)


def test_does_not_false_positive_on_column_named_like_forbidden_word():
    # This column name contains "UPDATE" as a substring but is NOT the SQL keyword.
    # Word-boundary matching should NOT block this.
    result = execute_readonly_sql("SELECT 1 AS updated_at_check;")
    assert isinstance(result, list), f"False positive: blocked a harmless query. Got: {result}"


def test_reports_syntax_error_gracefully_instead_of_crashing():
    result = execute_readonly_sql("SELECT * FROM this_table_does_not_exist;")
    assert "error" in result