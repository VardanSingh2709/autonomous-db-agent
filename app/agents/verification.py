import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query

TOLERANCE = 0.02  # allow up to 2% difference for rounding


def verify_root_cause_claim(region: str, product: str, claimed_q2: float, claimed_q3: float) -> dict:
    """
    Independently re-queries the database for the EXACT combination of
    region + product the agent claimed, and checks its numbers against
    what the agent submitted. This never trusts the agent's arithmetic.
    """
    sql = """
    SELECT
        SUM(CASE WHEN order_date >= '2024-04-01' AND order_date < '2024-07-01'
                 THEN oi.quantity * oi.unit_price END) AS q2_revenue,
        SUM(CASE WHEN order_date >= '2024-07-01' AND order_date < '2024-10-01'
                 THEN oi.quantity * oi.unit_price END) AS q3_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    JOIN products p ON p.id = oi.product_id
    JOIN regions r ON r.id = o.region_id
    WHERE r.name = :region AND p.name = :product;
    """
    result = run_query(sql, {"region": region, "product": product})

    if not result or result[0]["q2_revenue"] is None:
        return {
            "verified": False,
            "reason": f"No orders found for product '{product}' in region '{region}'. "
                      f"The claimed region/product combination may not exist."
        }

    actual_q2 = float(result[0]["q2_revenue"] or 0)
    actual_q3 = float(result[0]["q3_revenue"] or 0)

    q2_matches = abs(actual_q2 - claimed_q2) <= (actual_q2 * TOLERANCE + 0.01)
    q3_matches = abs(actual_q3 - claimed_q3) <= (actual_q3 * TOLERANCE + 0.01)

    if q2_matches and q3_matches:
        return {"verified": True, "actual_q2": actual_q2, "actual_q3": actual_q3}

    return {
        "verified": False,
        "reason": f"Claimed Q2/Q3 revenue for {product} in {region} was "
                  f"{claimed_q2}/{claimed_q3}, but the database actually shows "
                  f"{actual_q2}/{actual_q3}. Please re-check your query.",
        "actual_q2": actual_q2,
        "actual_q3": actual_q3
    }