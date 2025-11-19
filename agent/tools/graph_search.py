import os
from neo4j import GraphDatabase

class Neo4jConnection:
    """A class to manage the connection to the Neo4j database."""
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def search(self, search_term: str, limit: int = 5) -> list[dict]:
        """Executes a search query against the graph database."""
        

        with self.driver.session() as session:
            # This is a basic query. A real-world application would have a more
            # sophisticated way to parse the user's query and build a Cypher query.
            result = session.run(
                """
                MATCH (n)
                                WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $search_term)
                RETURN n
                LIMIT $limit
                """,
                                search_term=search_term,
                limit=limit
            )
            print(result)
            # The result records are not directly serializable, so we convert them.
            return [dict(record["n"]) for record in result]

def get_neo4j_connection():
    """Establishes a connection to the Neo4j database."""
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER")
    password = os.environ.get("NEO4J_PASSWORD")
    return Neo4jConnection(uri, user, password)

def graphsearch(search_term: str, limit: int = 5) -> list[dict]:
    """Searches for entities and relationships in the graph database."""
    neo4j_conn = get_neo4j_connection()
    try:
        results = neo4j_conn.search(search_term, limit)
    finally:
        neo4j_conn.close()
    
    return results
