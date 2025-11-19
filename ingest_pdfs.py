import os
import argparse
import psycopg2
from pgvector.psycopg2 import register_vector
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# --- Database Connection Setup ---
def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB", "vectordb"),
        user=os.environ.get("POSTGRES_USER", "user"),
        password=os.environ.get("POSTGRES_PASSWORD", "password"),
        host=os.environ.get("POSTGRES_HOST", "localhost")
    )

def get_neo4j_driver():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))

# --- PDF Processing ---
def extract_text_from_pdf(file_stream):
    reader = PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def add_document_to_db(doc_id, content, subject, model):
    """Adds a single document to both PostgreSQL and Neo4j."""
    pg_conn = None
    neo4j_driver = None
    try:
        # --- PostgreSQL Ingestion ---
        pg_conn = get_db_connection()
        register_vector(pg_conn)
        cur = pg_conn.cursor()
        embedding = model.encode(content)
        cur.execute(
            "INSERT INTO documents (id, subject, content, embedding) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET subject = EXCLUDED.subject, content = EXCLUDED.content, embedding = EXCLUDED.embedding;",
            (doc_id, subject, content, embedding)
        )
        pg_conn.commit()
        cur.close()

        # --- Neo4j Ingestion ---
        neo4j_driver = get_neo4j_driver()
        with neo4j_driver.session() as session:
            session.run(
                "MERGE (d:Document {id: $id}) SET d.subject = $subject MERGE (s:Subject {name: $subject}) MERGE (d)-[:IS_ABOUT]->(s)",
                id=doc_id, subject=subject
            )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if pg_conn: pg_conn.close()
        if neo4j_driver: neo4j_driver.close()

def main(pdfs_dir, subject):
    """Main function to ingest PDF documents from a directory."""
    print(f"Starting ingestion of PDFs from '{pdfs_dir}' for subject '{subject}'...")

    if not os.path.isdir(pdfs_dir):
        print(f"Error: Directory '{pdfs_dir}' not found.")
        return

    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    processed_files = 0
    for filename in os.listdir(pdfs_dir):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(pdfs_dir, filename)
            print(f"Processing '{filename}'...")
            try:
                with open(file_path, 'rb') as f:
                    content = extract_text_from_pdf(f)
                
                doc_id = os.path.splitext(filename)[0]
                result = add_document_to_db(doc_id, content, subject, model)
                
                if result.get("status") == "success":
                    print(f"  -> Successfully ingested '{doc_id}'.")
                    processed_files += 1
                else:
                    print(f"  -> Failed to ingest '{doc_id}': {result.get('message')}")
            except Exception as e:
                print(f"  -> An error occurred while processing {filename}: {e}")

    print(f"\nIngestion finished. Processed {processed_files} PDF file(s).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDF documents from a directory.")
    parser.add_argument("--dir", default="data/pdfs", help="Directory for PDFs. Defaults to 'data/pdfs'.")
    parser.add_argument("--subject", required=True, help="Subject for the documents.")
    args = parser.parse_args()
    main(args.dir, args.subject)
