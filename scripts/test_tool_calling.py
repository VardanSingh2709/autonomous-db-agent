import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

import time
from google.genai import errors as genai_errors


def send_message_with_retry(chat, message: str, max_attempts: int = 3):
    """Sends a chat message, retrying on temporary server errors."""
    for attempt in range(1, max_attempts + 1):
        try:
            return chat.send_message(message)
        except genai_errors.ServerError:
            if attempt == max_attempts:
                raise
            wait_seconds = attempt * 5
            print(f"Gemini temporarily unavailable (attempt {attempt}/{max_attempts}). Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tools.schema_tool import inspect_schema
from app.tools.sql_tool import execute_readonly_sql

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Register our real Python functions as tools the model is allowed to call.
config = types.GenerateContentConfig(
    tools=[inspect_schema, execute_readonly_sql]
)

question = "How many customers do we have in the North region?"

chat = client.chats.create(model="gemini-3.6-flash", config=config)
response = send_message_with_retry(chat, question)

print("Final answer:")
print(response.text)

print("\nFull conversation history (to see what tools were called):")
for message in chat.get_history():
    role = message.role
    for part in message.parts:
        if part.function_call:
            print(f"[{role}] CALLED TOOL: {part.function_call.name}({dict(part.function_call.args)})")
        elif part.function_response:
            print(f"[{role}] TOOL RESULT: {part.function_response.response}")
        elif part.text:
            print(f"[{role}] TEXT: {part.text}")
