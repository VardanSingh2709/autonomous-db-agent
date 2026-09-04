import os
import sys
import time
import json
from dotenv import load_dotenv
from groq import Groq, RateLimitError, InternalServerError, APIConnectionError, BadRequestError


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.tools.schema_tool import inspect_schema
from app.tools.sql_tool import execute_readonly_sql
from app.agents.verification import verify_revenue_decline_claim


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"

# Map tool names to the real Python functions that implement them.
AVAILABLE_TOOLS = {
    "inspect_schema": inspect_schema,
    "execute_readonly_sql": execute_readonly_sql,
}

# Groq (like most non-Gemini APIs) needs an explicit JSON schema per tool,
# rather than inferring one from a Python function automatically.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_schema",
            "description": "Returns the list of tables and columns in the database. Call this first, before writing any SQL.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_readonly_sql",
            "description": "Executes a read-only SELECT query and returns the results. Never use INSERT, UPDATE, DELETE, DROP, or any statement that modifies data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A single PostgreSQL SELECT statement."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "submit_final_answer",
        "description": "Submit your final, verified conclusion once you have enough evidence. Only call this when you are confident and have checked the specific combination of region and product responsible for the change, not just each dimension separately.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A plain-English explanation of the finding, 2-4 sentences."
                },
                "overall_q2_revenue": {"type": "number"},
                "overall_q3_revenue": {"type": "number"},
                "root_cause_region": {
                    "type": "string",
                    "description": "The single region most responsible for the decline."
                },
                "root_cause_product": {
                    "type": "string",
                    "description": "The single product most responsible for the decline, within that region."
                },
                "root_cause_q2_revenue": {
                    "type": "number",
                    "description": "Revenue for this specific product, in this specific region, in Q2."
                },
                "root_cause_q3_revenue": {
                    "type": "number",
                    "description": "Revenue for this specific product, in this specific region, in Q3."
                }
            },
            "required": [
                "summary", "overall_q2_revenue", "overall_q3_revenue",
                "root_cause_region", "root_cause_product",
                "root_cause_q2_revenue", "root_cause_q3_revenue"
            ]
        }
    }
},
]

SYSTEM_INSTRUCTION = """You are a careful data analyst investigating a business question
using a PostgreSQL database. Always inspect the schema before writing SQL if you
haven't already. Use execute_readonly_sql to test hypotheses step by step, drilling
down from high-level numbers to specific causes.

When investigating a change in a metric like revenue, consider breaking it down by
standard business dimensions such as region, product, product category, and customer
segment, not just by time period, since the root cause is often concentrated in one
specific slice rather than spread evenly.

Once you have enough evidence to confidently answer the question, respond with a
final plain-text answer and do not call any more tools."""


def call_with_retry(fn, *args, max_attempts=4, **kwargs):
    """Retries on rate limits, transient server/connection errors, and malformed
    tool-call generations (a known gpt-oss quirk on Groq)."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except (RateLimitError, InternalServerError, APIConnectionError) as e:
            if attempt == max_attempts:
                raise
            wait_seconds = attempt * 5
            print(f"Groq temporarily unavailable ({type(e).__name__}), attempt {attempt}/{max_attempts}. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)
        except BadRequestError as e:
            is_malformed_tool_call = "tool_use_failed" in str(e)
            if not is_malformed_tool_call or attempt == max_attempts:
                raise
            print(f"Model produced a malformed tool call (known gpt-oss quirk), attempt {attempt}/{max_attempts}. Retrying...")
            time.sleep(2)


def investigate(question: str, max_steps: int = 12):
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": question}
    ]
    trace = []

    for step in range(max_steps):
        response = call_with_retry(
            client.chat.completions.create,
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            # The model produced plain text instead of using submit_final_answer.
            # We don't accept this as a verified final answer.
            messages.append({
                "role": "user",
                "content": "Please use the submit_final_answer tool to provide your conclusion, rather than plain text."
            })
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "submit_final_answer":
                print(f"Step {step + 1}: agent submitted final answer, verifying...")
                verification = verify_revenue_decline_claim(
                    region=tool_args["root_cause_region"],
                    product=tool_args["root_cause_product"],
                    claimed_q2=tool_args["root_cause_q2_revenue"],
                    claimed_q3=tool_args["root_cause_q3_revenue"],
                )
                trace.append({
                    "step": step + 1,
                    "tool": "submit_final_answer",
                    "args": tool_args,
                    "verification": verification,
                })

                if verification["verified"]:
                    return tool_args, trace  # SUCCESS: verified final answer

                # Verification failed: tell the agent why, let it try again.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps({
                        "verified": False,
                        "message": verification["reason"] + " Please investigate further and resubmit."
                    }),
                })
                continue

            # Handle inspect_schema / execute_readonly_sql as before
            tool_fn = AVAILABLE_TOOLS[tool_name]
            print(f"Step {step + 1}: calling {tool_name}({tool_args})")
            result = tool_fn(**tool_args)
            trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result),
            })

    return {"summary": "Investigation stopped: reached maximum steps without a verified answer."}, trace


if __name__ == "__main__":
    answer, trace = investigate("Why did revenue decline in Q3?")

    print("\n=== FINAL ANSWER ===")
    print(json.dumps(answer, indent=2))

    print(f"\n=== TRACE ({len(trace)} steps) ===")
    for entry in trace:
        print(f"Step {entry['step']}: {entry['tool']}({entry.get('args')})")
        if "verification" in entry:
            print(f"  -> verification: {entry['verification']}")
        else:
            print(f"  -> {entry.get('result')}")