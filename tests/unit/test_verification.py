import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.agents.verification import verify_aggregate_claim, _values_match


def test_values_match_exact():
    assert _values_match(100.0, 100.0) is True


def test_values_match_within_tolerance():
    # 2% tolerance + small flat buffer
    assert _values_match(100.0, 101.5) is True


def test_values_match_rejects_large_difference():
    assert _values_match(100.0, 150.0) is False


def test_verify_aggregate_claim_correct_case():
    result = verify_aggregate_claim(
        sql="SELECT COUNT(*) AS total FROM regions",
        params={},
        claimed_values={"total": 4}
    )
    assert result["verified"] is True


def test_verify_aggregate_claim_incorrect_case():
    result = verify_aggregate_claim(
        sql="SELECT COUNT(*) AS total FROM regions",
        params={},
        claimed_values={"total": 999}
    )
    assert result["verified"] is False
    assert "reason" in result


def test_verify_aggregate_claim_nonexistent_combination():
    result = verify_aggregate_claim(
        sql="SELECT COUNT(*) AS total FROM regions WHERE name = :region",
        params={"region": "Atlantis"},
        claimed_values={"total": 5}
    )
    assert result["verified"] is False