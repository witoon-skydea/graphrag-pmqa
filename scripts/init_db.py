import os
import sys
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Add parent directory to system path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# PMQA structure file
PMQA_STRUCTURE_FILE = os.getenv("PMQA_STRUCTURE_FILE", "../data/pmqa_structure.json")

def connect_to_neo4j():
    """
    Connect to Neo4j database.
    
    Returns:
        Neo4j driver instance
    """
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        print(f"Connected to Neo4j at {NEO4J_URI}")
        return driver
    except Exception as e:
        print(f"Error connecting to Neo4j: {str(e)}")
        sys.exit(1)

def create_constraints(driver):
    """
    Create uniqueness constraints for the database.
    
    Args:
        driver: Neo4j driver instance
    """
    with driver.session() as session:
        try:
            # Check if constraints exist
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]
            
            # Create constraints if they don't exist
            if "category_id_unique" not in constraints:
                session.run("CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE")
                print("Created constraint for Category.id")
            
            if "subcategory_id_unique" not in constraints:
                session.run("CREATE CONSTRAINT subcategory_id_unique IF NOT EXISTS FOR (s:Subcategory) REQUIRE s.id IS UNIQUE")
                print("Created constraint for Subcategory.id")
                
            if "criteria_id_unique" not in constraints:
                session.run("CREATE CONSTRAINT criteria_id_unique IF NOT EXISTS FOR (c:Criteria) REQUIRE c.id IS UNIQUE")
                print("Created constraint for Criteria.id")
                
            if "document_id_unique" not in constraints:
                session.run("CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
                print("Created constraint for Document.id")
                
            if "chunk_id_unique" not in constraints:
                session.run("CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")
                print("Created constraint for Chunk.id")
                
        except Exception as e:
            print(f"Error creating constraints: {str(e)}")
            raise

def load_pmqa_structure(file_path):
    """
    Load PMQA structure from JSON file.
    
    Args:
        file_path: Path to the PMQA structure JSON file
        
    Returns:
        PMQA structure as a dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            pmqa_data = json.load(f)
        print(f"Loaded PMQA structure from {file_path}")
        return pmqa_data
    except Exception as e:
        print(f"Error loading PMQA structure: {str(e)}")
        sys.exit(1)

def create_pmqa_structure(driver, pmqa_data):
    """
    Create PMQA structure in Neo4j.
    
    Args:
        driver: Neo4j driver instance
        pmqa_data: PMQA structure as a dictionary
    """
    categories = pmqa_data.get("categories", [])
    
    with driver.session() as session:
        # First, clear existing structure
        try:
            session.run(
                """
                MATCH (n) 
                WHERE n:Category OR n:Subcategory OR n:Criteria 
                DETACH DELETE n
                """
            )
            print("Cleared existing PMQA structure")
        except Exception as e:
            print(f"Error clearing existing structure: {str(e)}")
            raise
        
        # Create categories, subcategories, and criteria
        for category in categories:
            # Create category
            try:
                session.run(
                    """
                    CREATE (c:Category {
                        id: $id,
                        name: $name,
                        description: $description
                    })
                    """,
                    id=category["id"],
                    name=category["name"],
                    description=category.get("description", "")
                )
                print(f"Created Category {category['id']}: {category['name']}")
                
                # Create subcategories
                subcategories = category.get("subcategories", [])
                for subcategory in subcategories:
                    try:
                        session.run(
                            """
                            MATCH (c:Category {id: $category_id})
                            CREATE (s:Subcategory {
                                id: $id,
                                name: $name,
                                description: $description,
                                category_id: $category_id
                            })
                            CREATE (c)-[:HAS_SUBCATEGORY]->(s)
                            """,
                            category_id=category["id"],
                            id=subcategory["id"],
                            name=subcategory["name"],
                            description=subcategory.get("description", "")
                        )
                        print(f"Created Subcategory {subcategory['id']}: {subcategory['name']}")
                        
                        # Create criteria
                        criteria = subcategory.get("criteria", [])
                        for criterion in criteria:
                            try:
                                session.run(
                                    """
                                    MATCH (s:Subcategory {id: $subcategory_id})
                                    CREATE (c:Criteria {
                                        id: $id,
                                        name: $name,
                                        description: $description,
                                        subcategory_id: $subcategory_id
                                    })
                                    CREATE (s)-[:HAS_CRITERIA]->(c)
                                    """,
                                    subcategory_id=subcategory["id"],
                                    id=criterion["id"],
                                    name=criterion["name"],
                                    description=criterion.get("description", "")
                                )
                                print(f"Created Criteria {criterion['id']}: {criterion['name']}")
                            except Exception as e:
                                print(f"Error creating criteria {criterion['id']}: {str(e)}")
                    except Exception as e:
                        print(f"Error creating subcategory {subcategory['id']}: {str(e)}")
            except Exception as e:
                print(f"Error creating category {category['id']}: {str(e)}")

def create_indices(driver):
    """
    Create indices for better query performance.
    
    Args:
        driver: Neo4j driver instance
    """
    with driver.session() as session:
        try:
            # Check if indices exist
            result = session.run("SHOW INDEXES")
            indices = [record["name"] for record in result if "name" in record]
            
            # Create indices if they don't exist
            if "document_title_index" not in indices:
                session.run("CREATE INDEX document_title_index IF NOT EXISTS FOR (d:Document) ON (d.title)")
                print("Created index for Document.title")
                
            if "document_category_index" not in indices:
                session.run("CREATE INDEX document_category_index IF NOT EXISTS FOR (d:Document) ON (d.category)")
                print("Created index for Document.category")
                
            if "chunk_content_index" not in indices:
                session.run("CREATE INDEX chunk_content_index IF NOT EXISTS FOR (c:Chunk) ON (c.content)")
                print("Created index for Chunk.content")
                
        except Exception as e:
            print(f"Error creating indices: {str(e)}")
            raise

def main():
    """
    Main function to initialize the Neo4j database.
    """
    print("Initializing Neo4j database...")
    
    # Connect to Neo4j
    driver = connect_to_neo4j()
    
    try:
        # Create constraints
        create_constraints(driver)
        
        # Create indices
        create_indices(driver)
        
        # Load PMQA structure
        pmqa_data = load_pmqa_structure(PMQA_STRUCTURE_FILE)
        
        # Create PMQA structure in Neo4j
        create_pmqa_structure(driver, pmqa_data)
        
        print("Neo4j database initialization completed successfully!")
    
    except Exception as e:
        print(f"Error initializing Neo4j database: {str(e)}")
    
    finally:
        # Close driver
        driver.close()

if __name__ == "__main__":
    main()
