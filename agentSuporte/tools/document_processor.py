import os
from io import BytesIO
from pypdf import PdfReader
import docx
import markdown
from sentence_transformers import SentenceTransformer

from .vector_search import get_db_connection
from .graph_search import get_neo4j_connection

# --- Text Extraction --- #

def extract_text_from_pdf(file_stream: BytesIO) -> str:
    reader = PdfReader(file_stream)
    text = "".join(page.extract_text() for page in reader.pages)
    return text

def extract_text_from_docx(file_stream: BytesIO) -> str:
    doc = docx.Document(file_stream)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text_from_txt(file_stream: BytesIO) -> str:
    return file_stream.read().decode('utf-8')

def extract_text_from_md(file_stream: BytesIO) -> str:
    md_content = file_stream.read().decode('utf-8')
    # A simple conversion to text; might need more sophisticated parsing for complex MD
    html = markdown.markdown(md_content)
    # This is a basic way to strip HTML, might need a library like BeautifulSoup
    import re
    return re.sub('<[^<]+?>', '', html)

EXTRACTORS = {
    '.pdf': extract_text_from_pdf,
    '.docx': extract_text_from_docx,
    '.txt': extract_text_from_txt,
    '.md': extract_text_from_md,
}

# --- Data Ingestion --- #

model = SentenceTransformer('all-MiniLM-L6-v2')

def add_document(doc_id: str, content: str, subject: str):
    """Adds a document to both vector and graph databases."""
    # Ingest into PostgreSQL
    pg_conn = get_db_connection()
    try:
        cur = pg_conn.cursor()
        embedding = model.encode(content)
        cur.execute(
            "INSERT INTO documents (id, subject, content, embedding) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET subject = EXCLUDED.subject, content = EXCLUDED.content, embedding = EXCLUDED.embedding;",
            (doc_id, subject, content, embedding)
        )
        pg_conn.commit()
        cur.close()
    finally:
        pg_conn.close()

    # Ingest into Neo4j
    neo4j_conn = get_neo4j_connection()
    try:
        with neo4j_conn.driver.session() as session:
            session.run(
                "MERGE (d:Document {id: $id}) SET d.name = $name, d.subject = $subject",
                id=doc_id, name=doc_id, subject=subject
            )
    finally:
        neo4j_conn.close()
    
    return {"status": "success", "doc_id": doc_id}

def remove_document(doc_id: str):
    """Removes a document from both vector and graph databases."""
    # Remove from PostgreSQL
    pg_conn = get_db_connection()
    try:
        cur = pg_conn.cursor()
        cur.execute("DELETE FROM documents WHERE id = %s;", (doc_id,))
        pg_conn.commit()
        deleted_count_pg = cur.rowcount
        cur.close()
    finally:
        pg_conn.close()

    # Remove from Neo4j
    neo4j_conn = get_neo4j_connection()
    try:
        with neo4j_conn.driver.session() as session:
            result = session.run(
                "MATCH (d:Document {id: $id}) DETACH DELETE d",
                id=doc_id
            )
            deleted_count_neo4j = result.summary().counters.nodes_deleted
    finally:
        neo4j_conn.close()

    if deleted_count_pg > 0 or deleted_count_neo4j > 0:
        return {"status": "success", "doc_id": doc_id, "message": "Document removed."}
    else:
        return {"status": "not_found", "doc_id": doc_id, "message": "Document not found."}

