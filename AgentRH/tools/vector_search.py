import os
from typing import Optional
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

# Initialize the sentence transformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')
_model = None

def get_model():
    global _model
    if _model is None:
        print("Carregando modelo SentenceTransformer...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Modelo carregado.")
    return _model

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST")
    )
    return conn

def vectorsearch(query: str, subject: Optional[str] = None, limit: int = 5) -> list[dict]:
    """Busca documentos relevantes no banco de dados vetorial, retornando uma lista de dicionários com os resultados.

    Cada dicionário contém 'id', 'subject', 'content' e 'similarity_score'.
    Opcionalmente, pode filtrar por 'subject'.
    """
    conn = get_db_connection()
    register_vector(conn)
    cur = conn.cursor()
    print("query savastane",query)

    
    # Gerar o embedding para a consulta
    model = get_model()
    query_embedding = model.encode(query)

    # Construir a consulta SQL dinamicamente
    base_query = "SELECT id, subject, content, 1 - (embedding <=> %s) AS similarity_score FROM documents"
    params = [query_embedding]
    where_clauses = []

    if subject:
        where_clauses.append("subject = %s")
        params.append(subject)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " ORDER BY similarity_score DESC LIMIT %s"
    params.append(limit)

    cur.execute(base_query, tuple(params))
    
    # Mapear os resultados para uma lista de dicionários
    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "subject": row[1],
            "content": row[2],
            "similarity_score": round(row[3], 4)
        })

    cur.close()
    conn.close()

    return results
