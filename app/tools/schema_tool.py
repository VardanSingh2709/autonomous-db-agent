import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query


def inspect_schema() -> list:
    """
    Returns the list of tables and their columns in the database.
    The agent should call this first, before writing any SQL,
    to know what tables and columns actually exist.
    """
    sql = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    return run_query(sql)