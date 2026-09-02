import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load variables from .env into the environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# An "engine" manages a pool of database connections.
# We create it once and reuse it everywhere else in the app.
engine = create_engine(DATABASE_URL)


def test_connection():
    """Runs a trivial query to confirm we can reach the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()
    

def run_query(sql: str, params: dict = None):
    """
    Executes a SQL query and returns the results as a list of dictionaries.

    sql: the SQL string to run, with optional named placeholders like :region
    params: a dictionary of values to safely substitute into those placeholders

    Example:
        run_query("SELECT * FROM regions WHERE name = :region", {"region": "North"})
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    value = test_connection()
    print(f"Connection successful. Test query returned: {value}")

    regions = run_query("SELECT * FROM regions")
    print("Regions:", regions)

    north_only = run_query("SELECT * FROM regions WHERE name = :region", {"region": "North"})
    print("Filtered:", north_only)