import os
import sys
import time
import json
from dotenv import load_dotenv
from groq import Groq, RateLimitError, InternalServerError, APIConnectionError, BadRequestError

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.tools.schema_tool import inspect_schema
from app.tools.sql_tool import execute_readonly_sql
from app.agents.verification import (
    verify_revenue_decline_claim,
    verify_churn_claim,
    verify_conversion_decline_claim,
    verify_purchase_frequency_claim,
    verify_product_mix_claim,
)

load_dotenv()
from app.database.connection import get_secret
client = Groq(api_key=get_secret("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

AVAILABLE_TOOLS = {
    "inspect_schema": inspect_schema,
    "execute_readonly_sql": execute_readonly_sql,
}


# Fetch the schema ONCE at module load time, since it doesn't change during
# a session. This saves the agent one full step (an LLM call + tool round-trip)
# on every single investigation, since it no longer needs to "discover" the
# same static schema over and over.
_CACHED_SCHEMA = inspect_schema()

def _format_schema_for_prompt(schema_rows):
    tables = {}
    for row in schema_rows:
        tables.setdefault(row["table_name"], []).append(f"{row['column_name']} ({row['data_type']})")
    lines = []
    for table, columns in tables.items():
        lines.append(f"- {table}({', '.join(columns)})")
    return "\n".join(lines)

_SCHEMA_TEXT = _format_schema_for_prompt(_CACHED_SCHEMA)

BASE_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_schema",
            "description": "Returns the list of tables and columns in the database. Call this first, before writing any SQL.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_readonly_sql",
            "description": "Executes a read-only SELECT query and returns the results. Never use INSERT, UPDATE, DELETE, DROP, or any statement that modifies data.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "A single PostgreSQL SELECT statement."}},
                "required": ["query"]
            }
        }
    }
]

SYSTEM_INSTRUCTION = f"""You are a careful data analyst investigating a business question
using a PostgreSQL database. All data in this database is from the year 2024, with
Q2 = April-June 2024 and Q3 = July-September 2024.

The database schema is already known — you do NOT need to call inspect_schema first.
Here it is:

{_SCHEMA_TEXT}

Use execute_readonly_sql to test hypotheses step by step, drilling down from
high-level numbers to specific causes.

When investigating a change in a metric, consider breaking it down by standard
business dimensions such as region, product, product category, customer segment,
or marketing channel, since the root cause is often concentrated in one specific
slice rather than spread evenly. When a metric is a rate or ratio (like churn rate
or average order value), be careful to compute the correct numerator and denominator.

IMPORTANT: When determining whether a record (e.g. a subscription) was active AT A
SPECIFIC PAST DATE, do not filter by its CURRENT status column. A record's status
reflects its state now, not at that past date — a subscription that has since been
cancelled may still have been active on an earlier date. To check "active as of
date X", use only: start_date <= X AND (end_date IS NULL OR end_date >= X). Do not
add "AND status = 'active'" to this kind of query, since that incorrectly excludes
records that were active at X but have since changed status.

IMPORTANT: If a question is vague or underspecified (e.g. it does not say which
metric, dimension, or time period to look at), you cannot ask a follow-up question
in this setting. Instead, you MUST explicitly state, as the first sentence of your
answer, which specific interpretation you chose and why.

Once you have enough evidence, submit your answer using the provided submit tool.
Do not answer in plain text."""


# --- Scenario configuration: one entry per question type we can investigate ---
SCENARIOS = {
    "revenue_decline": {
        "submit_tool": {
            "type": "function",
            "function": {
                "name": "submit_final_answer",
                "description": "Submit your final conclusion. Must identify the specific region AND product combination responsible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "root_cause_region": {"type": "string"},
                        "root_cause_product": {"type": "string"},
                        "root_cause_q2_revenue": {"type": "number"},
                        "root_cause_q3_revenue": {"type": "number"},
                    },
                    "required": ["summary", "root_cause_region", "root_cause_product", "root_cause_q2_revenue", "root_cause_q3_revenue"]
                }
            }
        },
        "verify": lambda args: verify_revenue_decline_claim(
            args["root_cause_region"], args["root_cause_product"],
            args["root_cause_q2_revenue"], args["root_cause_q3_revenue"]
        )
    },
    "churn_increase": {
        "submit_tool": {
            "type": "function",
            "function": {
                "name": "submit_final_answer",
                "description": "Submit your final conclusion. Must identify the specific subscription tier responsible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "root_cause_tier": {"type": "string"},
                        "root_cause_q2_churn_pct": {"type": "number"},
                        "root_cause_q3_churn_pct": {"type": "number"},
                    },
                    "required": ["summary", "root_cause_tier", "root_cause_q2_churn_pct", "root_cause_q3_churn_pct"]
                }
            }
        },
        "verify": lambda args: verify_churn_claim(
            args["root_cause_tier"], args["root_cause_q2_churn_pct"], args["root_cause_q3_churn_pct"]
        )
    },
    "conversion_decline": {
        "submit_tool": {
            "type": "function",
            "function": {
                "name": "submit_final_answer",
                "description": "Submit your final conclusion. Must identify the specific marketing channel responsible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "root_cause_channel": {"type": "string"},
                        "root_cause_q2_orders": {"type": "number"},
                        "root_cause_q3_orders": {"type": "number"},
                    },
                    "required": ["summary", "root_cause_channel", "root_cause_q2_orders", "root_cause_q3_orders"]
                }
            }
        },
        "verify": lambda args: verify_conversion_decline_claim(
            args["root_cause_channel"], args["root_cause_q2_orders"], args["root_cause_q3_orders"]
        )
    },
    "purchase_frequency_drop": {
        "submit_tool": {
            "type": "function",
            "function": {
                "name": "submit_final_answer",
                "description": "Submit your final conclusion. Must identify whether returning or new customers are responsible.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "root_cause_customer_type": {"type": "string", "description": "'returning' or 'new'"},
                        "root_cause_q2_avg_orders": {"type": "number"},
                        "root_cause_q3_avg_orders": {"type": "number"},
                    },
                    "required": ["summary", "root_cause_customer_type", "root_cause_q2_avg_orders", "root_cause_q3_avg_orders"]
                }
            }
        },
        "verify": lambda args: verify_purchase_frequency_claim(
            args["root_cause_customer_type"], args["root_cause_q2_avg_orders"], args["root_cause_q3_avg_orders"]
        )
    },
    "product_mix_effect": {
        "submit_tool": {
            "type": "function",
            "function": {
                "name": "submit_final_answer",
                "description": "Submit your final conclusion about the average order value change.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "q2_avg_order_value": {"type": "number"},
                        "q3_avg_order_value": {"type": "number"},
                        "q2_avg_items_per_order": {"type": "number"},
                        "q3_avg_items_per_order": {"type": "number"},
                    },
                    "required": ["summary", "q2_avg_order_value", "q3_avg_order_value", "q2_avg_items_per_order", "q3_avg_items_per_order"]
                }
            }
        },
        "verify": lambda args: verify_product_mix_claim(
            args["q2_avg_order_value"], args["q3_avg_order_value"],
            args["q2_avg_items_per_order"], args["q3_avg_items_per_order"]
        )
    },
}


GENERAL_SUBMIT_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_answer",
        "description": "Submit your final answer to the question — a number, name, or short fact.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The final answer, as a plain value (e.g. '60', 'North', '17997.75')."},
                "explanation": {"type": "string", "description": "One sentence on how you found this."},
                "stated_assumption": {
                    "type": "string",
                    "description": "REQUIRED if the question was ambiguous or underspecified: state which specific interpretation you chose. Leave empty if the question was already unambiguous."
                }
            },
            "required": ["answer", "explanation", "stated_assumption"]
        }
    }
}


def investigate_general(question: str, max_steps: int = 15):
    tool_schemas = BASE_TOOL_SCHEMAS + [GENERAL_SUBMIT_TOOL]
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": question}
    ]
    trace = []

    for step in range(max_steps):
        response = call_with_retry(
            client.chat.completions.create,
            model=MODEL, messages=messages, tools=tool_schemas,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            # Capture the plain-text response instead of discarding it —
            # this may be a legitimate refusal, not just a formatting slip.
            trace.append({"step": step + 1, "tool": None, "plain_text_response": message.content})
            messages.append({"role": "user", "content": "Please use the submit_answer tool, not plain text."})
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "submit_answer":
                trace.append({"step": step + 1, "tool": tool_name, "args": tool_args})
                return tool_args, trace

            tool_fn = AVAILABLE_TOOLS[tool_name]
            result = tool_fn(**tool_args)
            trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "result": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": json.dumps(result)})

    return {"answer": None, "explanation": "Reached max steps without submitting."}, trace


def call_with_retry(fn, *args, max_attempts=4, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args, **kwargs)
        except RateLimitError as e:
            if "tokens per day" in str(e) or "TPD" in str(e):
                # Daily quota exhausted — no amount of short retrying will help today.
                raise RuntimeError(f"Daily token quota exhausted. Stop and resume tomorrow. Original error: {e}") from e
            if attempt == max_attempts:
                raise
            wait_seconds = attempt * 5
            print(f"Groq temporarily unavailable (per-minute rate limit), attempt {attempt}/{max_attempts}. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)
        except (InternalServerError, APIConnectionError) as e:
            if attempt == max_attempts:
                raise
            wait_seconds = attempt * 5
            print(f"Groq temporarily unavailable ({type(e).__name__}), attempt {attempt}/{max_attempts}. Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)
        except BadRequestError as e:
             is_recoverable_parse_issue = "tool_use_failed" in str(e) or "output_parse_failed" in str(e)
             if not is_recoverable_parse_issue or attempt == max_attempts:
                raise
             print(f"Model produced unparseable output, attempt {attempt}/{max_attempts}. Retrying...")
             time.sleep(2)


def investigate(question: str, scenario_key: str, max_steps: int = 15, on_step=None):
    scenario = SCENARIOS[scenario_key]
    tool_schemas = BASE_TOOL_SCHEMAS + [scenario["submit_tool"]]
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": question}
    ]
    trace = []

    for step in range(max_steps):
        if on_step:
            on_step(f"Step {step + 1}: thinking...")

        response = call_with_retry(
            client.chat.completions.create,
            model=MODEL, messages=messages, tools=tool_schemas,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            messages.append({"role": "user", "content": "Please use the submit_final_answer tool, not plain text."})
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "submit_final_answer":
                if on_step:
                    on_step(f"Step {step + 1}: verifying final answer...")
                verification = scenario["verify"](tool_args)
                trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "verification": verification})
                if verification["verified"]:
                    return tool_args, trace
                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                    "content": json.dumps({"verified": False, "message": verification["reason"] + " Please investigate further and resubmit."})
                })
                continue

            if on_step:
                on_step(f"Step {step + 1}: running a database query...")
            tool_fn = AVAILABLE_TOOLS[tool_name]
            result = tool_fn(**tool_args)
            trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "result": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": json.dumps(result)})

    return {"summary": "Investigation stopped: reached maximum steps without a verified answer."}, trace


QUESTIONS = {
    "revenue_decline": "Why did revenue decline in Q3?",
    "churn_increase": "Why did churn increase in Q3?",
    "conversion_decline": "Why did conversion decline in Q3?",
    "purchase_frequency_drop": "Why are customers ordering less frequently in Q3?",
    "product_mix_effect": "Why did average order value change in Q3, even though no prices changed?",
}


COMPARISON_SUBMIT_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_comparison_answer",
        "description": "Submit your final answer for a Q2-vs-Q3 comparison question, as two separate numeric values.",
        "parameters": {
            "type": "object",
            "properties": {
                "q2_value": {"type": "number", "description": "The value for Q2 2024."},
                "q3_value": {"type": "number", "description": "The value for Q3 2024."},
                "explanation": {"type": "string"}
            },
            "required": ["q2_value", "q3_value", "explanation"]
        }
    }
}


def investigate_comparison(question: str, max_steps: int = 12):
    """Like investigate_general, but for Q2-vs-Q3 comparison questions, using a
    structured two-value submission instead of free text — avoids the ambiguity
    of parsing numbers back out of a sentence."""
    tool_schemas = BASE_TOOL_SCHEMAS + [COMPARISON_SUBMIT_TOOL]
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": question}
    ]
    trace = []

    for step in range(max_steps):
        response = call_with_retry(
            client.chat.completions.create,
            model=MODEL, messages=messages, tools=tool_schemas,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            messages.append({"role": "user", "content": "Please use the submit_comparison_answer tool, not plain text."})
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "submit_comparison_answer":
                trace.append({"step": step + 1, "tool": tool_name, "args": tool_args})
                return tool_args, trace

            tool_fn = AVAILABLE_TOOLS[tool_name]
            result = tool_fn(**tool_args)
            trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "result": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": json.dumps(result)})

    return {"q2_value": None, "q3_value": None, "explanation": "Reached max steps without submitting."}, trace


if __name__ == "__main__":

    scenario_key = sys.argv[1] if len(sys.argv) > 1 else "revenue_decline"
    question = QUESTIONS[scenario_key]

    print(f"=== Investigating: {question} ===\n")
    answer, trace = investigate(question, scenario_key)

    print("\n=== FINAL ANSWER ===")
    print(json.dumps(answer, indent=2))

    print(f"\n=== TRACE ({len(trace)} steps) ===")
    for entry in trace:
        print(f"Step {entry['step']}: {entry['tool']}({entry.get('args')})")
        if "verification" in entry:
            print(f"  -> verification: {entry['verification']}")
        else:
            print(f"  -> {entry.get('result')}")