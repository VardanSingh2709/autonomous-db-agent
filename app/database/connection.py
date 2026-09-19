import os
from decimal import Decimal
from datetime import date, datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
import streamlit as st

load_dotenv()


def get_secret(key):
    """Reads from Streamlit secrets when deployed, falls back to .env locally."""
    try:
        return st.secrets[key]
    except (FileNotFoundError, KeyError, st.errors.StreamlitAPIException):
        return os.getenv(key)


DATABASE_URL = get_secret("DATABASE_URL")
AGENT_DATABASE_URL = get_secret("AGENT_DATABASE_URL")

# Admin engine — used by local scripts (seeding, benchmarking, ground truth
# generation). Never used by the agent itself. Not present in production
# secrets, so this will be None when deployed — that's expected and correct.
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# Agent engine — used exclusively by the agent's tools, through the
# restricted read-only role. This is the ONLY engine the deployed app needs.
agent_engine = create_engine(AGENT_DATABASE_URL)


@event.listens_for(agent_engine, "connect")
def set_statement_timeout(dbapi_connection, connection_record):
    """
    Sets a 10-second query timeout on every new connection. We set this
    AFTER connecting (via SET), not as a startup parameter, because Neon's
    pooled connection endpoint (PgBouncer) rejects statement_timeout passed
    as a startup option.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("SET statement_timeout = 10000")
    cursor.close()


def _make_json_safe(value):
    """Converts database-specific types into plain JSON-friendly types."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def run_query(sql: str, params: dict = None):
    """Admin query function — uses the full-access postgres role. Local use only."""
    with engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [
            {key: _make_json_safe(value) for key, value in row.items()}
            for row in rows
        ]


def run_agent_query(sql: str, params: dict = None, max_rows: int = 500):
    """
    The ONLY function agent tools should use to touch the database.
    Uses the restricted read-only role, a 10-second query timeout (set via
    the connect event above), and a 500-row result cap.
    """
    with agent_engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        rows = result.mappings().all()
        if len(rows) > max_rows:
            rows = rows[:max_rows]
        return [
            {key: _make_json_safe(value) for key, value in row.items()}
            for row in rows
        ]