import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

dotenv_path = find_dotenv()

load_dotenv(dotenv_path)

OPENAI_INSIGHTBOT_API_KEY = os.getenv("OPENAI_INSIGHTBOT_API_KEY")