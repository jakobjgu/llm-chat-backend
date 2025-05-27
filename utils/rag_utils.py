import os
import re
from docx import Document
import pdfplumber


# Loaders
def load_markdown_files(directory):
    docs = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            path = os.path.join(directory, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                docs.append({
                    "source": filename,
                    "content": text
                })
    return docs

def load_docx(path):
    doc = Document(path)
    return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def load_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Chunkers
def chunk_markdown(text, max_tokens=300):
    # Split by heading or paragraph
    raw_chunks = re.split(r"(?:\n\s*#+|\n{2,})", text)
    chunks = []
    current = ""

    for chunk in raw_chunks:
        if len((current + chunk).split()) < max_tokens:
            current += " " + chunk
        else:
            if current.strip():
                chunks.append(current.strip())
            current = chunk
    if current.strip():
        chunks.append(current.strip())

    return chunks

def chunk_plaintext(text, max_tokens=300):
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len((current + para).split()) < max_tokens:
            current += " " + para
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para
    if current.strip():
        chunks.append(current.strip())

    return chunks

# Unified Interface
def load_and_chunk_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".md":
        text = open(path).read()
        return chunk_markdown(text)
    elif ext == ".txt":
        text = open(path).read()
        return chunk_plaintext(text)
    elif ext == ".docx":
        text = load_docx(path)
        return chunk_plaintext(text)
    elif ext == ".pdf":
        text = load_pdf(path)
        return chunk_plaintext(text)
