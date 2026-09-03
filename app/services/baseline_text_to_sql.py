import time
import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import errors as genai_errors


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.database.connection import run_query

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini_with_retry(prompt: str, max_attempts: int = 3) -> str:
    """Calls Gemini, retrying on temporary server errors with increasing delays."""
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            return response.text.strip()
        except genai_errors.ServerError as e:
            if attempt == max_attempts:
                raise  # out of retries, let the real error surface
            wait_seconds = attempt * 5  # 5s, then 10s, then 15s...
            print(f"Gemini is temporarily unavailable (attempt {attempt}/{max_attempts}). Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

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


def generate_sql(question: str) -> str:
    prompt = f"""You are a SQL expert. Given this database schema:

{SCHEMA_DESCRIPTION}

Write a single PostgreSQL SELECT query to answer this question:
"{question}"

Return ONLY the SQL query, with no explanation, no markdown formatting, no backticks."""
    return call_gemini_with_retry(prompt)


def summarize_result(question: str, sql: str, result: list) -> str:
    prompt = f"""A user asked: "{question}"

We ran this SQL query:
{sql}

It returned this data:
{result}

Write a concise, plain-English answer to the user's question based on this data."""
    return call_gemini_with_retry(prompt)


def answer_question(question: str):
    """The full baseline pipeline: question -> SQL -> execute -> answer."""
    start = time.time()

    print("Generating SQL...")
    sql = generate_sql(question)
    print(f"Generated SQL ({time.time() - start:.1f}s so far):\n{sql}\n")

    print("Running query...")
    result = run_query(sql)
    print(f"Query result ({time.time() - start:.1f}s so far):\n{result}\n")

    print("Summarizing result...")
    answer = summarize_result(question, sql, result)
    print(f"Final answer ({time.time() - start:.1f}s total):\n{answer}")


if __name__ == "__main__":
    answer_question("What was our total revenue in Q3 2024?")