from typing import List, Dict, Any, Optional, Tuple, BinaryIO
import os
import uuid
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mimetypes
import json

from loguru import logger

from app.core.config import settings
from app.db.file_system import file_storage
from app.db.graph_db import graph_db
from app.db.vector_db import vector_db
from app.services.embedding_service import embedding_service
from app.services.entity_service import entity_service
from app.utils.text_splitters import split_text_by_chunk


class DocumentProcessor:
    """
    Processes uploaded documents: extracts text, analyzes content, creates embeddings,
    and stores in graph and vector databases.
    """

    def __init__(self):
        """
        Initialize the document processor.
        """
        self.processing_queue = asyncio.Queue()
        self.processing_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=2)  # Limit concurrent processing
        self._initialize_directories()

    def _initialize_directories(self):
        """
        Initialize necessary directories.
        """
        # Ensure logs directory exists
        os.makedirs("../logs", exist_ok=True)

    async def start_processing_worker(self):
        """
        Start the background worker to process documents from the queue.
        """
        logger.info("Starting document processing worker")
        while True:
            try:
                document_id, file_path, metadata = await self.processing_queue.get()
                logger.info(f"Processing document {document_id} from queue")
                
                # Update status to "processing"
                self.processing_tasks[document_id] = {
                    "status": "processing",
                    "start_time": datetime.now().isoformat(),
                    "progress": 0
                }
                
                # Process document in a separate thread to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    self._process_document,
                    document_id,
                    file_path,
                    metadata
                )
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in processing worker: {str(e)}")
                # Wait a bit before continuing to avoid rapid failures
                await asyncio.sleep(1)

    def queue_document(
        self, 
        document_id: str, 
        file_path: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Queue a document for processing.
        
        Args:
            document_id: Document ID
            file_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            Processing status
        """
        asyncio.create_task(self.processing_queue.put((document_id, file_path, metadata)))
        
        # Track the task
        self.processing_tasks[document_id] = {
            "status": "queued",
            "queue_time": datetime.now().isoformat(),
            "progress": 0
        }
        
        logger.info(f"Document {document_id} queued for processing")
        return self.get_processing_status(document_id)

    def get_processing_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get the status of a document processing task.
        
        Args:
            document_id: Document ID
            
        Returns:
            Processing status
        """
        if document_id not in self.processing_tasks:
            return {
                "document_id": document_id,
                "status": "not_found",
                "message": "Document not found in processing queue"
            }
        
        task_info = self.processing_tasks[document_id]
        return {
            "document_id": document_id,
            "status": task_info.get("status", "unknown"),
            "message": task_info.get("message", ""),
            "start_time": task_info.get("start_time"),
            "end_time": task_info.get("end_time"),
            "progress": task_info.get("progress", 0),
            "error": task_info.get("error")
        }

    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from a document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text
        """
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Extract text based on MIME type
        text = ""
        
        try:
            # For now, just read as text - we'll implement proper extractors later
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            # Return empty string if extraction fails
            return ""

    def _process_document(
        self, 
        document_id: str, 
        file_path: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """
        Process a document: extract text, analyze content, create embeddings, and store in databases.
        
        This is executed in a separate thread.
        
        Args:
            document_id: Document ID
            file_path: Path to the document file
            metadata: Document metadata
        """
        try:
            # Update progress
            self._update_task_progress(document_id, 10, "Extracting text from document")
            
            # Extract text from document
            text = self._extract_text_from_file(file_path)
            if not text:
                raise ValueError(f"Failed to extract text from document {file_path}")
            
            # Update progress
            self._update_task_progress(document_id, 20, "Analyzing document content")
            
            # Analyze document content to identify PMQA categories
            analysis_result = entity_service.analyze_document(text, document_id)
            
            # Update progress
            self._update_task_progress(document_id, 30, "Splitting document into chunks")
            
            # Split document into chunks
            chunks, chunk_metadatas = self._split_document(text, document_id, metadata, analysis_result)
            
            # Update progress
            self._update_task_progress(document_id, 40, "Creating document embedding")
            
            # Create document embedding
            document_embedding = embedding_service.create_embedding(text)
            
            # Update progress
            self._update_task_progress(document_id, 50, "Creating chunk embeddings")
            
            # Create chunk embeddings
            chunk_embeddings = embedding_service.create_embeddings(chunks)
            
            # Update progress
            self._update_task_progress(document_id, 60, "Storing document in vector database")
            
            # Store document in vector database
            vector_db.add_document(document_id, text, metadata)
            
            # Update progress
            self._update_task_progress(document_id, 70, "Storing chunks in vector database")
            
            # Store chunks in vector database
            chunk_ids = vector_db.add_chunks(chunks, chunk_metadatas, document_id)
            
            # Update progress
            self._update_task_progress(document_id, 80, "Creating document node in graph database")
            
            # Create document node in graph database
            self._create_document_node(document_id, metadata, analysis_result)
            
            # Update progress
            self._update_task_progress(document_id, 90, "Creating chunk nodes in graph database")
            
            # Create chunk nodes in graph database
            self._create_chunk_nodes(document_id, chunks, chunk_ids, chunk_metadatas)
            
            # Move document to appropriate category
            if "category" in metadata and metadata["category"].startswith("หมวด_"):
                file_storage.move_document_to_category(
                    file_path, 
                    metadata["category"],
                    os.path.basename(file_path)
                )
            
            # Update task status to completed
            self._update_task_completed(document_id, "Document processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            self._update_task_failed(document_id, str(e))

    def _update_task_progress(
        self, 
        document_id: str, 
        progress: float, 
        message: str
    ) -> None:
        """
        Update the progress of a processing task.
        
        Args:
            document_id: Document ID
            progress: Progress percentage (0-100)
            message: Progress message
        """
        if document_id in self.processing_tasks:
            self.processing_tasks[document_id].update({
                "progress": progress,
                "message": message
            })
            logger.debug(f"Document {document_id} processing progress: {progress}% - {message}")

    def _update_task_completed(
        self, 
        document_id: str, 
        message: str
    ) -> None:
        """
        Update task status to completed.
        
        Args:
            document_id: Document ID
            message: Completion message
        """
        if document_id in self.processing_tasks:
            self.processing_tasks[document_id].update({
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "progress": 100,
                "message": message
            })
            logger.info(f"Document {document_id} processing completed: {message}")

    def _update_task_failed(
        self, 
        document_id: str, 
        error: str
    ) -> None:
        """
        Update task status to failed.
        
        Args:
            document_id: Document ID
            error: Error message
        """
        if document_id in self.processing_tasks:
            self.processing_tasks[document_id].update({
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "error": error,
                "message": f"Processing failed: {error}"
            })
            logger.error(f"Document {document_id} processing failed: {error}")

    def _split_document(
        self, 
        text: str, 
        document_id: str, 
        metadata: Dict[str, Any], 
        analysis_result: Dict[str, Any]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Split document into chunks for processing.
        
        Args:
            text: Document text
            document_id: Document ID
            metadata: Document metadata
            analysis_result: Analysis result from entity service
            
        Returns:
            Tuple containing list of chunks and list of chunk metadata dictionaries
        """
        # Split text into chunks
        chunks = split_text_by_chunk(
            text, 
            chunk_size=settings.CHUNK_SIZE, 
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Create metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "document_id": document_id,
                "start_idx": i * (settings.CHUNK_SIZE - settings.CHUNK_OVERLAP) if i > 0 else 0,
                "end_idx": (i + 1) * settings.CHUNK_SIZE - (i * settings.CHUNK_OVERLAP),
                "pmqa_references": analysis_result.get("pmqa_references", [])
            })
            chunk_metadatas.append(chunk_metadata)
        
        return chunks, chunk_metadatas

    def _create_document_node(
        self, 
        document_id: str, 
        metadata: Dict[str, Any], 
        analysis_result: Dict[str, Any]
    ) -> None:
        """
        Create a document node in the graph database.
        
        Args:
            document_id: Document ID
            metadata: Document metadata
            analysis_result: Analysis result from entity service
        """
        # Prepare document properties
        doc_properties = {
            "id": document_id,
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "path": metadata.get("file_path", ""),
            "mimetype": metadata.get("mimetype", ""),
            "author": metadata.get("author", ""),
            "published_date": metadata.get("published_date", ""),
            "created_at": metadata.get("created_at", datetime.now().isoformat()),
            "modified_at": metadata.get("modified_at", datetime.now().isoformat()),
            "processed": True
        }
        
        # Create document node
        create_document_query = """
        CREATE (d:Document $properties)
        RETURN d
        """
        graph_db.execute_write_query(create_document_query, {"properties": doc_properties})
        
        # Create relationships to PMQA structure
        if "pmqa_references" in analysis_result:
            for ref in analysis_result["pmqa_references"]:
                # Determine the appropriate level (category, subcategory, criteria)
                if "criteria_id" in ref:
                    # Link to criteria
                    link_query = """
                    MATCH (d:Document {id: $document_id})
                    MATCH (c:Criteria {id: $criteria_id})
                    CREATE (d)-[:RELATES_TO]->(c)
                    """
                    graph_db.execute_write_query(link_query, {
                        "document_id": document_id,
                        "criteria_id": ref["criteria_id"]
                    })
                elif "subcategory_id" in ref:
                    # Link to subcategory
                    link_query = """
                    MATCH (d:Document {id: $document_id})
                    MATCH (s:Subcategory {id: $subcategory_id})
                    CREATE (d)-[:RELATES_TO]->(s)
                    """
                    graph_db.execute_write_query(link_query, {
                        "document_id": document_id,
                        "subcategory_id": ref["subcategory_id"]
                    })
                elif "category_id" in ref:
                    # Link to category
                    link_query = """
                    MATCH (d:Document {id: $document_id})
                    MATCH (c:Category {id: $category_id})
                    CREATE (d)-[:RELATES_TO]->(c)
                    """
                    graph_db.execute_write_query(link_query, {
                        "document_id": document_id,
                        "category_id": ref["category_id"]
                    })

    def _create_chunk_nodes(
        self, 
        document_id: str, 
        chunks: List[str], 
        chunk_ids: List[str], 
        chunk_metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Create chunk nodes in the graph database.
        
        Args:
            document_id: Document ID
            chunks: List of text chunks
            chunk_ids: List of chunk IDs
            chunk_metadatas: List of chunk metadata dictionaries
        """
        for i, (chunk, chunk_id, metadata) in enumerate(zip(chunks, chunk_ids, chunk_metadatas)):
            # Prepare chunk properties
            chunk_properties = {
                "id": chunk_id,
                "document_id": document_id,
                "content": chunk[:500],  # Store truncated content in graph
                "vector_id": chunk_id,
                "start_idx": metadata.get("start_idx", 0),
                "end_idx": metadata.get("end_idx", 0)
            }
            
            # Create chunk node and link to document
            create_chunk_query = """
            MATCH (d:Document {id: $document_id})
            CREATE (c:Chunk $properties)
            CREATE (d)-[:HAS_CHUNK]->(c)
            RETURN c
            """
            graph_db.execute_write_query(create_chunk_query, {
                "document_id": document_id,
                "properties": chunk_properties
            })
            
            # Create relationships to PMQA structure
            if "pmqa_references" in metadata:
                for ref in metadata["pmqa_references"]:
                    # Determine the appropriate level (category, subcategory, criteria)
                    if "criteria_id" in ref:
                        # Link to criteria
                        link_query = """
                        MATCH (c:Chunk {id: $chunk_id})
                        MATCH (cr:Criteria {id: $criteria_id})
                        CREATE (c)-[:RELATES_TO]->(cr)
                        """
                        graph_db.execute_write_query(link_query, {
                            "chunk_id": chunk_id,
                            "criteria_id": ref["criteria_id"]
                        })
                    elif "subcategory_id" in ref:
                        # Link to subcategory
                        link_query = """
                        MATCH (c:Chunk {id: $chunk_id})
                        MATCH (s:Subcategory {id: $subcategory_id})
                        CREATE (c)-[:RELATES_TO]->(s)
                        """
                        graph_db.execute_write_query(link_query, {
                            "chunk_id": chunk_id,
                            "subcategory_id": ref["subcategory_id"]
                        })
                    elif "category_id" in ref:
                        # Link to category
                        link_query = """
                        MATCH (c:Chunk {id: $chunk_id})
                        MATCH (cat:Category {id: $category_id})
                        CREATE (c)-[:RELATES_TO]->(cat)
                        """
                        graph_db.execute_write_query(link_query, {
                            "chunk_id": chunk_id,
                            "category_id": ref["category_id"]
                        })


# Create a singleton instance
document_processor = DocumentProcessor()
