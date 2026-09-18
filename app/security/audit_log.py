import json
import time
import os

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "audit.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def log_query(query: str, outcome: str):
    """Appends one line per executed (or refused) query. Never logs credentials."""
    entry = {
        "timestamp": time.time(),
        "query": query,
        "outcome": outcome,  # "executed" or "refused"
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")