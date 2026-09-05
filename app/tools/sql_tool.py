import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query
from sqlalchemy.exc import ProgrammingError


def execute_readonly_sql(query: str) -> list | dict:
    """
    Executes a read-only SQL SELECT query and returns the results. Only use
    SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, or any
    statement that modifies data. If the query has a syntax or reference
    error, you will receive an error message back — read it carefully,
    fix the specific issue, and try again.
    """
    try:
        return run_query(query)
    except ProgrammingError as e:
        # Extract just Postgres's own error message, not the full Python traceback,
        # since that's the useful, actionable part for the model to read.
        return {"error": str(e.orig)}