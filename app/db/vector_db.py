from typing import Dict, List, Optional, Any
import os
import uuid

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from loguru import logger

from app.core.config import settings


class ChromaDatabase:
    """
    Manages connection and operations for ChromaDB vector database.
    """

    def __init__(self):
        """
        Initialize ChromaDB connection using settings.
        """
        self.client = None
        self.embedding_function = None
        self.documents_collection = None
        self.chunks_collection = None
        self.connect()

    def connect(self) -> None:
        """
        Connect to ChromaDB and initialize collections.
        """
        try:
            # Ensure persist directory exists
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            # Initialize client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            
            # Set up embedding function based on Ollama
            # Note: This is a placeholder and will need to be updated
            # with actual Ollama embedding function
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Initialize collections
            self.documents_collection = self.get_or_create_collection("documents")
            self.chunks_collection = self.get_or_create_collection("chunks")
            
            logger.info("Successfully connected to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {str(e)}")
            raise

    def get_or_create_collection(self, name: str):
        """
        Get or create a collection in ChromaDB.
        
        Args:
            name: Collection name
            
        Returns:
            ChromaDB collection
        """
        try:
            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata={"description": f"Collection for {name} in PMQA GraphRAG system"}
            )
        except Exception as e:
            logger.error(f"Error getting or creating collection {name}: {str(e)}")
            raise

    def add_document(
        self,
        document_id: str,
        document_text: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a document to the documents collection.
        
        Args:
            document_id: Unique document ID
            document_text: Full document text
            metadata: Document metadata
        """
        try:
            self.documents_collection.add(
                ids=[document_id],
                documents=[document_text],
                metadatas=[metadata]
            )
            logger.info(f"Added document {document_id} to vector database")
        except Exception as e:
            logger.error(f"Error adding document to vector database: {str(e)}")
            raise

    def add_chunks(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str
    ) -> List[str]:
        """
        Add document chunks to the chunks collection.
        
        Args:
            chunks: List of text chunks
            metadatas: List of metadata dictionaries for each chunk
            document_id: Parent document ID
            
        Returns:
            List of generated chunk IDs
        """
        chunk_ids = [f"chunk-{uuid.uuid4()}" for _ in range(len(chunks))]
        
        # Add document_id to all metadatas
        for metadata in metadatas:
            metadata["document_id"] = document_id
            
        try:
            self.chunks_collection.add(
                ids=chunk_ids,
                documents=chunks,
                metadatas=metadatas
            )
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
            return chunk_ids
        except Exception as e:
            logger.error(f"Error adding chunks to vector database: {str(e)}")
            raise

    def search_documents(
        self,
        query_text: str,
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            where_filter: Filter for document metadata
            
        Returns:
            Search results
        """
        try:
            results = self.documents_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
            logger.info(f"Document search for '{query_text[:50]}...' returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise

    def search_chunks(
        self,
        query_text: str,
        n_results: int = 10,
        where_filter: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            where_filter: Filter for chunk metadata
            
        Returns:
            Search results
        """
        try:
            results = self.chunks_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
            logger.info(f"Chunk search for '{query_text[:50]}...' returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            raise

    def delete_document(self, document_id: str) -> None:
        """
        Delete a document and its chunks from the vector database.
        
        Args:
            document_id: Document ID to delete
        """
        try:
            # Delete the document
            self.documents_collection.delete(ids=[document_id])
            
            # Delete all chunks associated with this document
            self.chunks_collection.delete(
                where={"document_id": document_id}
            )
            
            logger.info(f"Deleted document {document_id} and its chunks from vector database")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def close(self) -> None:
        """
        Close ChromaDB connection.
        """
        # ChromaDB doesn't have an explicit close method
        logger.info("ChromaDB connection resources released")


# Create a singleton instance
vector_db = ChromaDatabase()


# Ensure clean shutdown
def close_db_connection():
    """
    Close database connection.
    """
    if vector_db is not None:
        vector_db.close()
