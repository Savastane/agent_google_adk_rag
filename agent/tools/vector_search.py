import os
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST")
    )
    return conn

def search(query: str, subject: str = None, limit: int = 5) -> list[str]:
    """Searches for relevant documents in the vector database, optionally filtering by subject."""
    conn = get_db_connection()
    register_vector(conn)
    cur = conn.cursor()

    # Generate embedding for the query
    query_embedding = model.encode(query)

    # Build the SQL query dynamically
    sql_query = "SELECT content FROM documents"
    params = []

    if subject:
        sql_query += " WHERE subject = %s"
        params.append(subject)
    
    sql_query += " ORDER BY embedding <=> %s LIMIT %s"
    params.append(query_embedding)
    params.append(limit)

    cur.execute(sql_query, tuple(params))
    results = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return results
