import sys, os, re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_agent_query
from app.security.audit_log import log_query
from sqlalchemy.exc import ProgrammingError

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]


def execute_readonly_sql(query: str) -> list | dict:
    """
    Executes a read-only SQL SELECT query and returns the results (max 500 rows).
    Only use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or any
    statement that modifies data. If the query has a syntax or reference error,
    you will receive an error message back — read it carefully, fix the issue,
    and try again.
    """
    stripped = query.strip().upper()

    if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
        log_query(query, "refused: not a SELECT/WITH statement")
        return {"error": "Refused: only SELECT (or WITH ... SELECT) statements are permitted."}

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", stripped):
            log_query(query, f"refused: forbidden keyword {keyword}")
            return {"error": f"Refused: query contains forbidden keyword '{keyword}'."}

    try:
        result = run_agent_query(query)
        log_query(query, "executed")
        return result
    except ProgrammingError as e:
        log_query(query, f"error: {e.orig}")
        return {"error": str(e.orig)}