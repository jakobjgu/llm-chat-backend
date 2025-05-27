import boto3
import pandas as pd
from decimal import Decimal
import tiktoken
from datetime import datetime

# Setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("InsightBotLogs")
encoding = tiktoken.encoding_for_model("gpt-4")

def to_float(val):
    return float(val) if isinstance(val, Decimal) else val

items = []
response = table.scan()
items.extend(response["Items"])
while "LastEvaluatedKey" in response:
    response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
    items.extend(response["Items"])

valid_logs = []
for item in items:
    if all(k in item for k in ("log_timings", "input_tokens", "bot_response")):
        try:
            openai_time = to_float(item["log_timings"].get("openai_response_received", 0))
            input_tokens = int(item["input_tokens"])
            reply = item["bot_response"]
            response_tokens = len(encoding.encode(reply))
            total_tokens = input_tokens + response_tokens
            timestamp_str = item.get("timestamp_iso") or item["sk"].split("_")[0].replace("TS#", "")
            timestamp = datetime.utcfromtimestamp(int(timestamp_str)) if timestamp_str.isdigit() else timestamp_str

            valid_logs.append({
                "timestamp": timestamp,
                "input_tokens": input_tokens,
                "response_tokens": response_tokens,
                "total_tokens": total_tokens,
                "openai_duration": openai_time,
                "reply_sample": reply[:80] + "..." if len(reply) > 80 else reply
            })
        except Exception:
            continue

df = pd.DataFrame(valid_logs)
print(df.head())
