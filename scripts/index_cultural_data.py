#!/usr/bin/env python3
import sqlite3
import json
import os
import re
from pathlib import Path

DB_PATH = "data/users.db"

def _rag_chunk_text(text, max_chars=700):
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not cleaned: return []
    parts = [p.strip() for p in re.split(r"\n{2,}", cleaned) if p.strip()]
    chunks = []
    buf = ""
    for part in parts:
        if not buf:
            buf = part
            continue
        if len(buf) + 2 + len(part) <= max_chars:
            buf = f"{buf}\n\n{part}"
        else:
            chunks.append(buf)
            buf = part
    if buf: chunks.append(buf)
    return chunks

def index_file(conn, title, source, content):
    cursor = conn.cursor()
    # Check if already indexed
    cursor.execute("SELECT id FROM rag_documents WHERE title = ?", (title,))
    if cursor.fetchone():
        print(f"Skipping {title}, already indexed.")
        return

    cursor.execute(
        "INSERT INTO rag_documents (title, source, mime_type) VALUES (?, ?, ?)",
        (title, source, "application/json"),
    )
    doc_id = cursor.lastrowid
    chunks = _rag_chunk_text(content)
    for idx, chunk in enumerate(chunks):
        cursor.execute(
            "INSERT INTO rag_chunks (document_id, chunk_index, content) VALUES (?, ?, ?)",
            (doc_id, idx, chunk),
        )
        chunk_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO rag_chunks_fts (content, chunk_id) VALUES (?, ?)",
            (chunk, chunk_id),
        )
    print(f"Indexed {title} with {len(chunks)} chunks.")

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Index Folktales
    folktales_path = Path("data/folktales.json")
    if folktales_path.exists():
        with open(folktales_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for story in data:
                content = f"Title: {story['title']} ({story['titleEn']})\nStory: {story['story']}\nMoral: {story['moralLesson']}"
                index_file(conn, f"Folktale: {story['title']}", "folktales.json", content)

    # 2. Index Cultural Expressions
    culture_path = Path("data/cultural-expressions.json")
    if culture_path.exists():
        with open(culture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                content = f"Expression: {item['expression']} ({item['meaning']})\nExplanation: {item['explanation']}\nCultural Context: {item['culturalContext']}"
                index_file(conn, f"Culture: {item['expression']}", "cultural-expressions.json", content)

    # 3. Enable RAG in settings
    cursor = conn.cursor()
    cursor.execute("UPDATE rag_settings SET enabled = 1 WHERE id = 1")
    
    conn.commit()
    conn.close()
    print("Cultural indexing complete and RAG enabled.")

if __name__ == "__main__":
    main()
