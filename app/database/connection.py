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


if __name__ == "__main__":
    value = test_connection()
    print(f"Connection successful. Test query returned: {value}")