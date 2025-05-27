import os
from openai import OpenAI
import time
from utils.rag_utils import load_markdown_files, chunk_markdown
import duckdb

# embedding helper
client = OpenAI(api_key=os.getenv("OPENAI_INSIGHTBOT_API_KEY"))

def get_embedding(text, model="text-embedding-3-small", retries=3):
    for attempt in range(retries):
        try:
            response = client.embeddings.create(model=model, input=text)
            return response.data[0].embedding
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise e

# embed chunks into local db
con = duckdb.connect("rag_embeddings.duckdb")
docs = load_markdown_files("RAG_source_docs")
all_inserted = 0
for doc in docs:
    chunks = chunk_markdown(doc["content"])
    for chunk in chunks:
        embedding = get_embedding(chunk)
        con.execute(
            "INSERT INTO rag_chunks VALUES (?, ?, ?)",
            (doc["source"], chunk, embedding)
        )
        all_inserted += 1

print(f"Inserted {all_inserted} embedded chunks into DuckDB.")
