import sys
sys.path.append('../')
from lambda_function import handle_request
import json

event = {
    "headers": {"X-Forwarded-For": "127.0.0.1"},
    "body": json.dumps({
        "message": "Tell me more about juggling database shards."
    })
}

response = handle_request(event)
print(json.dumps(response, indent=2))
