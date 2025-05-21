import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        user_input = body.get("message", "")

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # ✅ Enables frontend fetch from anywhere
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"reply": response.choices[0].message.content})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
