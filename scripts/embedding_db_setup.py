import duckdb

con = duckdb.connect("rag_embeddings.duckdb")

con.execute("""
CREATE TABLE IF NOT EXISTS rag_chunks (
    source TEXT,
    chunk TEXT,
    embedding DOUBLE[]
)
""")
