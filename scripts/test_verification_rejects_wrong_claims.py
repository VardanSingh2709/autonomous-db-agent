import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.agents.verification import verify_root_cause_claim

# Deliberately wrong numbers, to confirm verification actually rejects bad claims.
result = verify_root_cause_claim(
    region="North",
    product="Product A - Wireless Earbuds",
    claimed_q2=99999,   # deliberately wrong
    claimed_q3=1,       # deliberately wrong
)
print(result)

# A region/product combination that doesn't exist at all.
result2 = verify_root_cause_claim(
    region="North",
    product="Perfume",  # Perfume was never sold in North in our seed data
    claimed_q2=100,
    claimed_q3=100,
)
print(result2)