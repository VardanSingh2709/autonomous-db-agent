import os
import sys
import time
from dotenv import load_dotenv
from groq import Groq, RateLimitError, InternalServerError, APIConnectionError

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

SCHEMA_DESCRIPTION = """
Tables:
- regions(id, name)
- product_categories(id, name)
- products(id, name, category_id, price, cost)
- customers(id, name, email, region_id, signup_date, is_returning)
- marketing_campaigns(id, name, channel, start_date, end_date)
- orders(id, customer_id, campaign_id, region_id, order_date)
- order_items(id, order_id, product_id, quantity, unit_price)
- subscriptions(id, customer_id, tier, start_date, end_date, status)
- payments(id, subscription_id, amount, payment_date, status)

Revenue is calculated as SUM(order_items.quantity * order_items.unit_price).
"""


def call_with_retry(messages, max_attempts=4):
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(model=MODEL, messages=messages)
            return response.choices[0].message.content
        except RateLimitError as e:
            if "tokens per day" in str(e) or "TPD" in str(e):
                raise RuntimeError(f"Daily token quota exhausted. Original error: {e}") from e
            if attempt == max_attempts:
                raise
            time.sleep(attempt * 5)
        except (InternalServerError, APIConnectionError):
            if attempt == max_attempts:
                raise
            time.sleep(attempt * 5)


def generate_sql(question: str) -> str:
    prompt = f"""You are a SQL expert. Given this database schema:

{SCHEMA_DESCRIPTION}

Write a single PostgreSQL SELECT query to answer this question:
"{question}"

Return ONLY the SQL query, with no explanation, no markdown formatting, no backticks."""
    return call_with_retry([{"role": "user", "content": prompt}]).strip()


def summarize_result(question: str, sql: str, result: list) -> str:
    prompt = f"""A user asked: "{question}"

We ran this SQL query:
{sql}

It returned this data:
{result}

Write a concise, plain-English answer to the user's question based on this data."""
    return call_with_retry([{"role": "user", "content": prompt}]).strip()


def answer_question_for_benchmark(question: str):
    """Returns the baseline's answer as a dict, for benchmark grading. Never raises."""
    try:
        sql = generate_sql(question)
        result = run_query(sql)
        answer = summarize_result(question, sql, result)
        return {"answer": answer, "sql": sql}
    except Exception as e:
        return {"answer": None, "sql": None, "error": str(e)}


def answer_question(question: str):
    """Interactive/manual version — prints each step. Used for one-off testing."""
    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}\n")
    result = run_query(sql)
    print(f"Query result:\n{result}\n")
    answer = summarize_result(question, sql, result)
    print(f"Final answer:\n{answer}")


if __name__ == "__main__":
    answer_question("What was our total revenue in Q3 2024?")