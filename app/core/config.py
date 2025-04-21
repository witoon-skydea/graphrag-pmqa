import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings for the GraphRAG PMQA system.
    """
    # API Config
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "GraphRAG PMQA"
    
    # Document Storage
    DOCUMENTS_BASE_DIR: str = os.getenv("DOCUMENTS_BASE_DIR", "../data/documents")
    RAW_DOCUMENTS_DIR: str = os.path.join(DOCUMENTS_BASE_DIR, "raw")
    
    # Neo4j Config
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Chroma DB Config
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "../data/chroma_db")
    
    # Ollama Config
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    ENTITY_MODEL: str = os.getenv("ENTITY_MODEL", "llama3")
    
    # Claude API Config
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    # Chunk Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Search Configuration
    TOP_K_VECTOR: int = int(os.getenv("TOP_K_VECTOR", "5"))
    TOP_K_GRAPH: int = int(os.getenv("TOP_K_GRAPH", "5"))
    
    # PMQA Structure
    PMQA_STRUCTURE_FILE: str = os.getenv("PMQA_STRUCTURE_FILE", "../data/pmqa_structure.json")
    
    class Config:
        case_sensitive = True

settings = Settings()
