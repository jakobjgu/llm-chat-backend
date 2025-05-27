import boto3
import pandas as pd
from decimal import Decimal
from datetime import datetime

# Setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("InsightBotLogs")

def to_float(val):
    return float(val) if isinstance(val, Decimal) else val

timing_keys = [
    "start",
    "input_parsed",
    "embedding_generated",
    "rag_query_completed",
    "rag_context_generated",
    "rate_quota_checked",
    "openai_response_received"
]

items = []
response = table.scan()
items.extend(response["Items"])
# This block handles pagination in DynamoDB scan() operations.
while "LastEvaluatedKey" in response:
    response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
    items.extend(response["Items"])

timing_data = []
for item in items:
    if "log_timings" in item and all(k in item["log_timings"] for k in timing_keys):
        try:
            log = item["log_timings"]
            timestamp_str = item.get("timestamp_iso") or item["sk"].split("_")[0].replace("TS#", "")
            timestamp = (int(timestamp_str)).fromtimestamp(datetime.timezone.utc) if timestamp_str.isdigit() else timestamp_str

            steps = [to_float(log[k]) for k in timing_keys]
            durations = [round(steps[i] - steps[i - 1], 4) for i in range(1, len(steps))]

            timing_data.append({
                "timestamp": timestamp,
                **{timing_keys[i]: steps[i] for i in range(len(steps))},
                **{f"Δ_{timing_keys[i]}": durations[i - 1] for i in range(1, len(steps))}
            })
        except Exception:
            continue

df_durations = pd.DataFrame(timing_data)
print(df_durations.head())

