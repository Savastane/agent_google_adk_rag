import json
import os
import psycopg2
from pgvector.psycopg2 import register_vector
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB", "vectordb"),
        user=os.environ.get("POSTGRES_USER", "user"),
        password=os.environ.get("POSTGRES_PASSWORD", "password"),
        host=os.environ.get("POSTGRES_HOST", "localhost")
    )

def get_neo4j_driver():
    """Establishes a connection to the Neo4j database."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(user, password))

# --- Data Ingestion Logic ---
def ingest_postgres_data(conn, documents, model):
    """Ingests documents and their embeddings into PostgreSQL."""
    register_vector(conn)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, subject TEXT, content TEXT, embedding VECTOR(384));")

    for doc in documents:
        embedding = model.encode(doc['content'])
        cur.execute(
            "INSERT INTO documents (id, subject, content, embedding) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;", 
            (doc['id'], doc['subject'], doc['content'], embedding)
        )
    
    conn.commit()
    cur.close()
    print("PostgreSQL ingestion complete.")

def ingest_neo4j_data(driver, graph_data):
    """Ingests nodes and relationships into Neo4j."""
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")

        # Ingest nodes
        for node in graph_data['nodes']:
            session.run(
                f"CREATE (n:{node['label']} {{id: $id, name: $name}})",
                id=node['id'], name=node['properties']['name']
            )
        
        # Ingest relationships
        for rel in graph_data['relationships']:
            session.run(
                """
                MATCH (a {{id: $source}}), (b {{id: $target}})
                CREATE (a)-[:`{rel_type}`]->(b)
                """ .format(rel_type=rel['type']),
                source=rel['source'], target=rel['target']
            )
    print("Neo4j ingestion complete.")


def main():
    """Main function to run the data ingestion."""
    print("Starting data ingestion...")
    
    # Load sample data
    with open('data/sample_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize embedding model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Ingest data into PostgreSQL
    pg_conn = None
    try:
        pg_conn = get_db_connection()
        ingest_postgres_data(pg_conn, data['documents'], model)
    except Exception as e:
        print(f"Error during PostgreSQL ingestion: {e}")
    finally:
        if pg_conn:
            pg_conn.close()

    # Ingest data into Neo4j
    neo4j_driver = None
    try:
        neo4j_driver = get_neo4j_driver()
        ingest_neo4j_data(neo4j_driver, data['graph'])
    except Exception as e:
        print(f"Error during Neo4j ingestion: {e}")
    finally:
        if neo4j_driver:
            neo4j_driver.close()
            
    print("Data ingestion finished.")

if __name__ == "__main__":
    main()
