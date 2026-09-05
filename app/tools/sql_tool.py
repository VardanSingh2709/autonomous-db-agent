import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query
from sqlalchemy.exc import ProgrammingError

# Minimal, keyword-based safety net. This is NOT a complete defense (Phase 14
# builds a proper one — a dedicated read-only database role, which blocks
# writes at the database level regardless of what SQL text looks like). This
# is just enough to stop obviously destructive statements before that exists.
FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]


def execute_readonly_sql(query: str) -> list | dict:
    """
    Executes a read-only SQL SELECT query and returns the results. Only use
    SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or any
    statement that modifies data. If the query has a syntax or reference
    error, you will receive an error message back — read it carefully,
    fix the specific issue, and try again.
    """
    upper_query = query.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in upper_query:
            return {"error": f"Refused: query contains forbidden keyword '{keyword}'. Only read-only SELECT statements are permitted."}

    try:
        return run_query(query)
    except ProgrammingError as e:
        return {"error": str(e.orig)}