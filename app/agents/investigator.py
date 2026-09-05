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
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

AVAILABLE_TOOLS = {
    "inspect_schema": inspect_schema,
    "execute_readonly_sql": execute_readonly_sql,
}

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

SYSTEM_INSTRUCTION = """You are a careful data analyst investigating a business question
using a PostgreSQL database. Always inspect the schema before writing SQL if you
haven't already. Use execute_readonly_sql to test hypotheses step by step, drilling
down from high-level numbers to specific causes.

When investigating a change in a metric, consider breaking it down by standard
business dimensions such as region, product, product category, customer segment,
or marketing channel, since the root cause is often concentrated in one specific
slice rather than spread evenly. When a metric is a rate or ratio (like churn rate
or average order value), be careful to compute the correct numerator and denominator.

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


def call_with_retry(fn, *args, max_attempts=4, **kwargs):
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
            print(f"Model produced a malformed tool call, attempt {attempt}/{max_attempts}. Retrying...")
            time.sleep(2)


def investigate(question: str, scenario_key: str, max_steps: int = 12):
    """Runs a full agentic investigation loop for a given question + scenario type."""
    scenario = SCENARIOS[scenario_key]
    tool_schemas = BASE_TOOL_SCHEMAS + [scenario["submit_tool"]]

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
            messages.append({"role": "user", "content": "Please use the submit_final_answer tool, not plain text."})
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            if tool_name == "submit_final_answer":
                print(f"Step {step + 1}: agent submitted final answer, verifying...")
                verification = scenario["verify"](tool_args)
                trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "verification": verification})

                if verification["verified"]:
                    return tool_args, trace

                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id, "name": tool_name,
                    "content": json.dumps({"verified": False, "message": verification["reason"] + " Please investigate further and resubmit."})
                })
                continue

            tool_fn = AVAILABLE_TOOLS[tool_name]
            print(f"Step {step + 1}: calling {tool_name}({tool_args})")
            result = tool_fn(**tool_args)
            trace.append({"step": step + 1, "tool": tool_name, "args": tool_args, "result": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": json.dumps(result)})

    return {"summary": "Investigation stopped: reached maximum steps without a verified answer."}, trace


if __name__ == "__main__":
    QUESTIONS = {
        "revenue_decline": "Why did revenue decline in Q3?",
        "churn_increase": "Why did churn increase in Q3?",
        "conversion_decline": "Why did conversion decline in Q3?",
        "purchase_frequency_drop": "Why are customers ordering less frequently in Q3?",
        "product_mix_effect": "Why did average order value change in Q3, even though no prices changed?",
    }

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