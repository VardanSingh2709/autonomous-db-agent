import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query

TOLERANCE = 0.02  # allow up to 2% difference, plus a small flat cent buffer


def _values_match(actual: float, claimed: float) -> bool:
    return abs(actual - claimed) <= (abs(actual) * TOLERANCE + 0.01)


def verify_aggregate_claim(sql: str, params: dict, claimed_values: dict) -> dict:
    """
    Generic verifier, reusable across every scenario type.

    sql/params: a query WE (the verification layer) write and control, independent
                of anything the agent computed, scoped to the agent's claimed
                dimension values (e.g. region='North', tier='Premium').
    claimed_values: maps result column name -> value the agent claimed, e.g.
                {"q2_revenue": 17997.75, "q3_revenue": 7999.0}
                or {"q2_churn_rate": 0.05, "q3_churn_rate": 0.22}

    This function doesn't know or care what business question is being checked —
    it just confirms actual database results match claimed numbers, column by column.
    """
    result = run_query(sql, params)

    if not result or all(v is None for v in result[0].values()):
        return {
            "verified": False,
            "reason": "No matching data found for the claimed combination. "
                      "The claimed dimension values may not exist."
        }

    row = result[0]
    mismatches = []
    actual_values = {}

    for column, claimed_value in claimed_values.items():
        actual_value = float(row.get(column) or 0)
        actual_values[column] = actual_value
        if not _values_match(actual_value, claimed_value):
            mismatches.append(f"{column}: claimed {claimed_value}, actual {actual_value}")

    if mismatches:
        return {
            "verified": False,
            "reason": "Mismatch(es) found: " + "; ".join(mismatches),
            "actual_values": actual_values
        }

    return {"verified": True, "actual_values": actual_values}


def verify_revenue_decline_claim(region: str, product: str, claimed_q2: float, claimed_q3: float) -> dict:
    """Scenario-specific wrapper for the revenue decline investigation."""
    sql = """
    SELECT
        SUM(CASE WHEN o.order_date >= '2024-04-01' AND o.order_date < '2024-07-01'
                 THEN oi.quantity * oi.unit_price END) AS q2_revenue,
        SUM(CASE WHEN o.order_date >= '2024-07-01' AND o.order_date < '2024-10-01'
                 THEN oi.quantity * oi.unit_price END) AS q3_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    JOIN products p ON p.id = oi.product_id
    JOIN regions r ON r.id = o.region_id
    WHERE r.name = :region AND p.name = :product;
    """
    return verify_aggregate_claim(
        sql=sql,
        params={"region": region, "product": product},
        claimed_values={"q2_revenue": claimed_q2, "q3_revenue": claimed_q3}
    )


def verify_churn_claim(tier: str, claimed_q2_rate: float, claimed_q3_rate: float) -> dict:
    """Scenario-specific wrapper for the churn increase investigation."""
    sql = """
    WITH q2_active AS (
        SELECT COUNT(*) AS active_start FROM subscriptions
        WHERE tier = :tier AND start_date < '2024-04-01'
          AND (end_date IS NULL OR end_date >= '2024-04-01')
    ),
    q2_cancelled AS (
        SELECT COUNT(*) AS cancelled FROM subscriptions
        WHERE tier = :tier AND status = 'cancelled'
          AND end_date >= '2024-04-01' AND end_date < '2024-07-01'
    ),
    q3_active AS (
        SELECT COUNT(*) AS active_start FROM subscriptions
        WHERE tier = :tier AND start_date < '2024-07-01'
          AND (end_date IS NULL OR end_date >= '2024-07-01')
    ),
    q3_cancelled AS (
        SELECT COUNT(*) AS cancelled FROM subscriptions
        WHERE tier = :tier AND status = 'cancelled'
          AND end_date >= '2024-07-01' AND end_date < '2024-10-01'
    )
    SELECT
        ROUND(q2c.cancelled::numeric / NULLIF(q2a.active_start, 0) * 100, 2) AS q2_churn_pct,
        ROUND(q3c.cancelled::numeric / NULLIF(q3a.active_start, 0) * 100, 2) AS q3_churn_pct
    FROM q2_active q2a, q2_cancelled q2c, q3_active q3a, q3_cancelled q3c;
    """
    return verify_aggregate_claim(
        sql=sql,
        params={"tier": tier},
        claimed_values={"q2_churn_pct": claimed_q2_rate, "q3_churn_pct": claimed_q3_rate}
    )


def verify_conversion_decline_claim(channel: str, claimed_q2_orders: float, claimed_q3_orders: float) -> dict:
    """Scenario-specific wrapper for the conversion decline investigation."""
    sql = """
    SELECT
        SUM(CASE WHEN o.order_date >= '2024-04-01' AND o.order_date < '2024-07-01' THEN 1 ELSE 0 END) AS q2_orders,
        SUM(CASE WHEN o.order_date >= '2024-07-01' AND o.order_date < '2024-10-01' THEN 1 ELSE 0 END) AS q3_orders
    FROM orders o
    JOIN marketing_campaigns mc ON o.campaign_id = mc.id
    WHERE mc.channel = :channel;
    """
    return verify_aggregate_claim(
        sql=sql,
        params={"channel": channel},
        claimed_values={"q2_orders": claimed_q2_orders, "q3_orders": claimed_q3_orders}
    )