import os
import shutil
from typing import List, Optional, Dict, Any, BinaryIO
from pathlib import Path
import uuid
from datetime import datetime

from loguru import logger

from app.core.config import settings


class FileSystemStorage:
    """
    Manages file storage operations for documents.
    """

    def __init__(self):
        """
        Initialize file system storage with configured base directory.
        """
        self.base_dir = settings.DOCUMENTS_BASE_DIR
        self.raw_dir = settings.RAW_DOCUMENTS_DIR
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """
        Ensure all required directories exist.
        """
        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Create raw directory if it doesn't exist
        os.makedirs(self.raw_dir, exist_ok=True)
        
        # Create category directories
        for category in range(1, 8):
            category_dir = os.path.join(self.base_dir, f"หมวด_{category}")
            os.makedirs(category_dir, exist_ok=True)
            
        logger.info(f"File system directories initialized at {self.base_dir}")

    def save_raw_document(
        self, 
        file: BinaryIO, 
        filename: str
    ) -> str:
        """
        Save an uploaded document to the raw directory.
        
        Args:
            file: File-like object
            filename: Original filename
            
        Returns:
            Path to the saved file
        """
        # Generate a unique filename to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{timestamp}_{unique_id}_{filename}"
        
        # Build the file path
        file_path = os.path.join(self.raw_dir, safe_filename)
        
        # Save the file
        try:
            with open(file_path, "wb") as f:
                # Read and write in chunks to handle large files
                chunk_size = 4096
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    
            logger.info(f"Document saved to raw directory: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving document to raw directory: {str(e)}")
            raise

    def move_document_to_category(
        self, 
        source_path: str, 
        category: str,
        new_filename: Optional[str] = None
    ) -> str:
        """
        Move a document from the raw directory to a category directory.
        
        Args:
            source_path: Path to the source file
            category: Target category (e.g., "หมวด_1")
            new_filename: Optional new filename
            
        Returns:
            Path to the moved file
        """
        # Validate category
        if not category.startswith("หมวด_") or not category[5:].isdigit():
            raise ValueError(f"Invalid category format: {category}")
            
        # Get category directory
        category_dir = os.path.join(self.base_dir, category)
        
        # Determine target filename
        if new_filename is None:
            new_filename = os.path.basename(source_path)
        
        # Build the target path
        target_path = os.path.join(category_dir, new_filename)
        
        # Move the file
        try:
            shutil.move(source_path, target_path)
            logger.info(f"Document moved to category {category}: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Error moving document to category {category}: {str(e)}")
            raise

    def delete_document(self, file_path: str) -> None:
        """
        Delete a document.
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Document deleted: {file_path}")
            else:
                logger.warning(f"Document not found: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def list_documents(
        self, 
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List documents in a category or all categories.
        
        Args:
            category: Optional category to list
            
        Returns:
            List of document info dictionaries
        """
        documents = []
        
        try:
            if category is not None:
                # List documents in a specific category
                category_dir = os.path.join(self.base_dir, category)
                if os.path.exists(category_dir):
                    for filename in os.listdir(category_dir):
                        file_path = os.path.join(category_dir, filename)
                        if os.path.isfile(file_path):
                            stat = os.stat(file_path)
                            documents.append({
                                "filename": filename,
                                "path": file_path,
                                "category": category,
                                "size": stat.st_size,
                                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
            else:
                # List documents in all categories
                for category_name in os.listdir(self.base_dir):
                    category_dir = os.path.join(self.base_dir, category_name)
                    if os.path.isdir(category_dir) and category_name.startswith("หมวด_"):
                        for filename in os.listdir(category_dir):
                            file_path = os.path.join(category_dir, filename)
                            if os.path.isfile(file_path):
                                stat = os.stat(file_path)
                                documents.append({
                                    "filename": filename,
                                    "path": file_path,
                                    "category": category_name,
                                    "size": stat.st_size,
                                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                                })
            
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    def list_raw_documents(self) -> List[Dict[str, Any]]:
        """
        List documents in the raw directory.
        
        Returns:
            List of document info dictionaries
        """
        documents = []
        
        try:
            for filename in os.listdir(self.raw_dir):
                file_path = os.path.join(self.raw_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    documents.append({
                        "filename": filename,
                        "path": file_path,
                        "category": "raw",
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Error listing raw documents: {str(e)}")
            raise

    def get_document_content(self, file_path: str) -> bytes:
        """
        Get the content of a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Document content as bytes
        """
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading document content: {str(e)}")
            raise


# Create a singleton instance
file_storage = FileSystemStorage()
