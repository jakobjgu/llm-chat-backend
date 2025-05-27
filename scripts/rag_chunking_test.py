from utils.rag_utils import load_markdown_files, chunk_markdown

docs = load_markdown_files("RAG_source_docs")
all_chunks = []

for doc in docs:
    chunks = chunk_markdown(doc["content"])
    for chunk in chunks:
        all_chunks.append({
            "source": doc["source"],
            "text": chunk
        })

print(f"Loaded {len(docs)} files → {len(all_chunks)} total chunks.")
