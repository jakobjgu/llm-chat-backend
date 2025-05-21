import os
import time
import json
import uuid
import boto3
import tiktoken
from datetime import datetime, timezone
from openai import OpenAI

# --- Constants ---
MODEL = "gpt-4o"
MODEL_MAX_TOKENS = 8192
MAX_RESPONSE_TOKENS = 300
MAX_INPUT_TOKENS = MODEL_MAX_TOKENS - MAX_RESPONSE_TOKENS
RATE_LIMIT_SECONDS = 10
QUOTA_LIMIT = 100  # per day

# --- Clients ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
dynamodb = boto3.resource("dynamodb")
log_table = dynamodb.Table("InsightBotLogs")
quota_table = dynamodb.Table("InsightBotQuotas")

# --- Globals ---
access_times = {}  # in-memory IP → timestamp
encoding = tiktoken.encoding_for_model("gpt-4")

# --- Helpers ---
def count_tokens(messages, encoding):
    return sum(len(encoding.encode(m["content"])) for m in messages)

def get_start_of_today_epoch():
    now = datetime.now(timezone.utc)
    today = datetime(now.year, now.month, now.day)
    return int(today.timestamp())

def build_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type"
    }

def build_error(error_type, message, status=400):
    return {
        "statusCode": status,
        "headers": build_headers(),
        "body": json.dumps({
            "error": {
                "type": error_type,
                "message": message
            }
        })
    }

# --- Lambda Entry ---
def lambda_handler(event, context):
    try:
        ip = event.get("headers", {}).get("X-Forwarded-For", "unknown")
        now = time.time()

        # Rate limit (in-memory)
        if now - access_times.get(ip, 0) < RATE_LIMIT_SECONDS:
            wait_time = int(RATE_LIMIT_SECONDS - (now - access_times[ip]))
            return build_error("RATE_LIMIT", f"You’ve hit the request limit. Please wait {wait_time} seconds.", 429)
        access_times[ip] = now

        # Parse input
        try:
            body = json.loads(event["body"])
            user_input = body.get("message", "").strip()

            if not user_input:
                return build_error("INVALID_INPUT", "The request body must include a non-empty 'message' field.")

        except (json.JSONDecodeError, TypeError):
            return build_error("INVALID_INPUT", "Malformed request body. Please send valid JSON with a 'message' field.")

        # Scope-aware system prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant specialized in the DC Metro Graph project, "
                    "the Stock Index Forecasting Project, and related Insight Data LLC work. "
                    "If the user asks anything outside that scope (e.g., politics, health, weather, personal info, job search), politely decline."
                )
            },
            {"role": "user", "content": user_input}
        ]

        # Token check
        total_prompt_tokens = count_tokens(messages, encoding)
        if total_prompt_tokens > MAX_INPUT_TOKENS:
            return build_error("TOO_MANY_TOKENS", f"Your prompt is too long ({total_prompt_tokens} tokens). Max allowed is {MAX_INPUT_TOKENS}.", 400)

        # Quota check
        quota_key = {"pk": f"IP#{ip}"}
        quota_record = quota_table.get_item(Key=quota_key).get("Item")
        reset_ts = get_start_of_today_epoch()

        if quota_record:
            if quota_record["last_reset_ts"] < reset_ts:
                quota_table.put_item(Item={**quota_key, "daily_count": 1, "last_reset_ts": reset_ts})
            elif quota_record["daily_count"] >= QUOTA_LIMIT:
                return build_error("QUOTA_EXCEEDED", f"Daily quota exceeded. Limit: {QUOTA_LIMIT} requests/day.", 429)
            else:
                quota_table.update_item(
                    Key=quota_key,
                    UpdateExpression="SET daily_count = daily_count + :inc",
                    ExpressionAttributeValues={":inc": 1}
                )
        else:
            quota_table.put_item(Item={**quota_key, "daily_count": 1, "last_reset_ts": reset_ts})

        # Generate response
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=MAX_RESPONSE_TOKENS
        )
        assistant_reply = response.choices[0].message.content

        # Log to DynamoDB
        log_table.put_item(Item={
            "pk": f"IP#{ip}",
            "sk": f"TS#{int(time.time())}_{uuid.uuid4()}",
            "user_input": user_input,
            "bot_response": assistant_reply,
            "model": MODEL,
            "input_tokens": total_prompt_tokens
        })

        return {
            "statusCode": 200,
            "headers": build_headers(),
            "body": json.dumps({"reply": assistant_reply})
        }

    except Exception as e:
        return build_error("INTERNAL_ERROR", f"Internal server error: {str(e)}", 500)
