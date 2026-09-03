import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query


def execute_readonly_sql(query: str) -> list:
    """
    Executes a read-only SQL SELECT query against the database and
    returns the results. Only use SELECT statements. Never use INSERT,
    UPDATE, DELETE, DROP, or any other statement that modifies data.
    """
    return run_query(query)