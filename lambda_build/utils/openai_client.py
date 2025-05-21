import os
from openai import OpenAI
from settings import OPENAI_INSIGHTBOT_API_KEY

client = OpenAI(api_key=OPENAI_INSIGHTBOT_API_KEY)

def get_openai_response(user_input):
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
    return response.choices[0].message.content