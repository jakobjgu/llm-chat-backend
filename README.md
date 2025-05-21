# InsightBot LLM Chat Backend

This is the serverless backend powering the InsightBot — a lightweight, secure, OpenAI-powered assistant integrated into [insightdatallc.com](https://insightdatallc.com). It responds to user questions related to the DC Metro Graph project, Stock Index Forecasting, and other scoped data science work, all via a floating chat UI on the website.

---

## Features

- **GPT-4o Assistant** via OpenAI API
- **AWS Lambda + API Gateway** (fully serverless)
- **Integrated into static React frontend hosted on S3**
- **Guardrails for safe, scoped usage**
- **Logging and quota tracking via DynamoDB**
- **Available site-wide as a floating chat bubble**

---

## Guardrails

This assistant is not a general-purpose chatbot. It’s scoped, rate-limited, and monitored.

| Protection            | Description                                                              |
|-----------------------|---------------------------------------------------------------------------|
| **Scope limiting**     | Refuses to answer questions outside its domain (via system prompt)       |
| **Rate limiting**      | Enforces one request every 10 seconds per user IP (in-memory)            |
| **Quota limiting**     | 100 requests per day per user IP, tracked in DynamoDB                   |
| **Token limits**       | Rejects user input exceeding token budget (based on OpenAI tokenizer)    |
| **Max output tokens**  | OpenAI response limited to 300 tokens                                    |
| **CORS protected**     | Only accepts requests from whitelisted frontend origins                 |

---

## Tech Stack

- **Backend**: Python + AWS Lambda + Boto3
- **Frontend**: React (chat bubble available on all pages)
- **Deployment**: 
  - Lambda package built in Docker for compatibility (`sam/build-python3.11`)
  - Uploaded to S3 and deployed via API Gateway
- **Storage**:
  - `InsightBotLogs` table for storing messages (DynamoDB)
  - `InsightBotQuotas` table for per-IP daily usage tracking

---

## Project Structure

```bash
llm-chat-backend/
├── lambda_function.py       # Main handler with rate + quota logic
├── requirements.txt         # Dependencies (boto3, openai, tiktoken)
├── llm_chat_backend.zip     # Deployable zip (built via Docker)
```

---

## Testing

The Lambda function supports JSON input via API Gateway. Sample test cases include:

✅ Valid message

❌ Missing or empty message field

❌ Malformed JSON

❌ Exceeded token count

❌ Rate-limited or quota-exceeded IP

Use AWS Lambda test events or curl to simulate these.

---

## Logs & Monitoring

All requests and assistant responses are logged to a DynamoDB table (`InsightBotLogs`) with the following fields:

- `pk`: partition key (`IP#<ip-address>`)
- `sk`: sort key (`TS#<timestamp>_<uuid>`)
- `user_input`: the user's question
- `bot_response`: the assistant's reply (if valid)
- `input_tokens`: number of tokens in prompt
- `model`: the OpenAI model used

Quota usage is tracked separately in the `InsightBotQuotas` table:
- `pk`: partition key (`IP#<ip-address>`)
- `request_count`: number of requests made today
- `last_reset_ts`: UTC timestamp of the last daily reset

Logs can be queried via the AWS Console or the DynamoDB SDK.

---

## Known Limitations / Next Steps

This project is secure and production-ready, but currently omits:

- ❌ Persistent chat memory across sessions
- ❌ OpenAI response streaming (typing effect)
- ❌ UI markdown rendering (e.g., code blocks, bold text)
- ❌ Chat message persistence in frontend
- ❌ Admin dashboard for usage/log insights

These can be added incrementally as needs grow.

---

## Credits

Built by [Jakob Gutzmann](https://insightdatallc.com) as part of Insight Data LLC.

This project integrates:
- AWS Lambda
- OpenAI GPT-4o
- DynamoDB
- React + S3 frontend

Special thanks to the OpenAI ecosystem and the serverless community.

---

## 📜 License

MIT License

You’re free to use, modify, and share this project, as long as you preserve proper attribution and don’t use it to create general-purpose or mis-scoped AI assistants without appropriate guardrails.
