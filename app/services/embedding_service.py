from typing import List, Dict, Any, Optional
import requests
import numpy as np
from loguru import logger

from app.core.config import settings


class OllamaEmbeddingService:
    """
    Service for creating embeddings using Ollama's API.
    """

    def __init__(self):
        """
        Initialize the embedding service with configured model.
        """
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL
        self.embedding_url = f"{self.base_url}/api/embeddings"
        self.batch_size = 10  # Default batch size for processing multiple texts

    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as a list of floats
        """
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(self.embedding_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embedding", [])
            
            logger.debug(f"Created embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            # Return a zero vector as fallback
            return [0.0] * 384  # Default dimension for most embedding models

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            batch_embeddings = self._create_embeddings_batch(batch)
            embeddings.extend(batch_embeddings)
            logger.debug(f"Processed embedding batch {i//self.batch_size + 1}/{(len(texts)-1)//self.batch_size + 1}")
        
        return embeddings

    def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a batch of texts.
        
        Args:
            texts: Batch of input texts
            
        Returns:
            List of embedding vectors for the batch
        """
        embeddings = []
        
        for text in texts:
            embedding = self.create_embedding(text)
            embeddings.append(embedding)
        
        return embeddings

    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


# Alternative implementation using a mock service for testing
class MockEmbeddingService:
    """
    Mock embedding service for testing purposes.
    """

    def __init__(self):
        """
        Initialize the mock embedding service.
        """
        self.embedding_dim = 384
        logger.warning("Using mock embedding service - not suitable for production")

    def create_embedding(self, text: str) -> List[float]:
        """
        Create a mock embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Mock embedding vector
        """
        # Create deterministic but unique embedding based on text hash
        import hashlib
        
        # Get hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to a seed for random number generator
        seed = int(text_hash, 16) % (2**32)
        np.random.seed(seed)
        
        # Generate a random embedding
        embedding = np.random.uniform(-1, 1, self.embedding_dim)
        
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Create mock embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of mock embedding vectors
        """
        return [self.create_embedding(text) for text in texts]

    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


# Choose the actual implementation based on availability of Ollama
try:
    # Test if Ollama is available
    requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
    embedding_service = OllamaEmbeddingService()
    logger.info(f"Using Ollama embedding service with model {settings.EMBEDDING_MODEL}")
except Exception as e:
    logger.warning(f"Ollama service not available, using mock embedding service: {str(e)}")
    embedding_service = MockEmbeddingService()
