from typing import Dict, List, Optional, Union

from loguru import logger
from neo4j import GraphDatabase, Driver, Session, Result
from neo4j.exceptions import Neo4jError

from app.core.config import settings


class Neo4jDatabase:
    """
    Manages connection and queries to Neo4j database.
    """

    def __init__(self):
        """
        Initialize Neo4j connection using settings.
        """
        self._driver: Optional[Driver] = None
        self.connect()

    def connect(self) -> None:
        """
        Connect to Neo4j database.
        """
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            # Verify connection
            with self._driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    logger.info(f"Successfully connected to Neo4j database at {settings.NEO4J_URI}")
                else:
                    logger.error("Failed to verify Neo4j connection")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j database: {str(e)}")
            self._driver = None
            raise

    def close(self) -> None:
        """
        Close Neo4j connection.
        """
        if self._driver is not None:
            self._driver.close()
            logger.info("Neo4j connection closed")
            self._driver = None

    def get_session(self) -> Session:
        """
        Get a Neo4j session.
        """
        if self._driver is None:
            logger.warning("No active Neo4j connection, attempting to reconnect")
            self.connect()
        
        if self._driver is None:
            raise ConnectionError("Could not establish connection to Neo4j")
            
        return self._driver.session()

    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict] = None
    ) -> Result:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            params: Query parameters
            
        Returns:
            Neo4j Result object
        """
        if params is None:
            params = {}
            
        with self.get_session() as session:
            try:
                result = session.run(query, params)
                return result
            except Neo4jError as e:
                logger.error(f"Neo4j query error: {str(e)}")
                raise

    def execute_read_query(
        self, 
        query: str, 
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Execute a read-only Cypher query and return results as a list of dictionaries.
        
        Args:
            query: Cypher query string
            params: Query parameters
            
        Returns:
            List of dictionaries containing the query results
        """
        if params is None:
            params = {}
            
        with self.get_session() as session:
            try:
                result = session.run(query, params)
                return [record.data() for record in result]
            except Neo4jError as e:
                logger.error(f"Neo4j read query error: {str(e)}")
                raise

    def execute_write_query(
        self, 
        query: str, 
        params: Optional[Dict] = None
    ) -> Result:
        """
        Execute a write Cypher query.
        
        Args:
            query: Cypher query string
            params: Query parameters
            
        Returns:
            Neo4j Result object
        """
        if params is None:
            params = {}
            
        with self.get_session() as session:
            try:
                result = session.run(query, params)
                return result
            except Neo4jError as e:
                logger.error(f"Neo4j write query error: {str(e)}")
                raise

    def create_pmqa_structure(self, pmqa_data: Dict) -> None:
        """
        Create PMQA structure in Neo4j.
        
        Args:
            pmqa_data: Dictionary containing PMQA structure
        """
        # Implementation will depend on the exact structure of pmqa_data
        logger.info("Creating PMQA structure in Neo4j")
        pass  # Will implement later


# Create a singleton instance
graph_db = Neo4jDatabase()


# Ensure clean shutdown
def close_db_connection():
    """
    Close database connection.
    """
    if graph_db is not None:
        graph_db.close()
