import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from decimal import Decimal
from datetime import date, datetime



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
    

def _make_json_safe(value):
    """Converts database-specific types into plain JSON-friendly types."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def run_query(sql: str, params: dict = None):
    with engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [
            {key: _make_json_safe(value) for key, value in row.items()}
            for row in rows
        ]


if __name__ == "__main__":
    value = test_connection()
    print(f"Connection successful. Test query returned: {value}")

    regions = run_query("SELECT * FROM regions")
    print("Regions:", regions)

    north_only = run_query("SELECT * FROM regions WHERE name = :region", {"region": "North"})
    print("Filtered:", north_only)