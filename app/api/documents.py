from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, Path
from fastapi.responses import FileResponse

from app.core.config import settings
from app.db.file_system import file_storage
from app.models.document import Document, DocumentList, DocumentCreate, DocumentProcessingStatus
from app.services.document_processor import document_processor
from app.utils.metadata_extractors import extract_metadata_from_file


router = APIRouter()


@router.post("/", response_model=DocumentProcessingStatus, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """
    Upload a new document to the system.
    
    Args:
        file: Document file
        title: Document title (optional)
        description: Document description (optional)
        author: Document author (optional)
        category: PMQA category (e.g., "หมวด_1") (optional)
        tags: Comma-separated tags (optional)
    
    Returns:
        Document processing status
    """
    try:
        # Generate a unique document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Save the file to raw directory
        file_path = file_storage.save_raw_document(file.file, file.filename)
        
        # Extract metadata from file
        metadata = extract_metadata_from_file(file_path)
        
        # Add user-provided metadata
        if title:
            metadata["title"] = title
        if description:
            metadata["description"] = description
        if author:
            metadata["author"] = author
        if category:
            metadata["category"] = category
        if tags:
            metadata["tags"] = [tag.strip() for tag in tags.split(",")]
        
        # Ensure required metadata exists
        if "title" not in metadata:
            metadata["title"] = os.path.splitext(file.filename)[0]
        if "mimetype" not in metadata:
            metadata["mimetype"] = file.content_type
        
        # Add document ID and timestamps
        metadata["id"] = document_id
        metadata["file_path"] = file_path
        metadata["created_at"] = datetime.now().isoformat()
        metadata["modified_at"] = datetime.now().isoformat()
        
        # Queue document for processing
        processing_status = document_processor.queue_document(
            document_id, file_path, metadata
        )
        
        return processing_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/", response_model=DocumentList)
async def list_documents(
    category: Optional[str] = Query(None, description="Filter by PMQA category"),
    author: Optional[str] = Query(None, description="Filter by author"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip")
):
    """
    List documents in the system.
    
    Args:
        category: Filter by PMQA category (optional)
        author: Filter by author (optional)
        keyword: Filter by keyword (optional)
        limit: Maximum number of documents to return (default: 10)
        offset: Number of documents to skip (default: 0)
    
    Returns:
        List of documents
    """
    try:
        # Get documents from file storage
        documents = []
        
        if category:
            # Get documents from specific category
            documents = file_storage.list_documents(category)
        else:
            # Get documents from all categories
            documents = file_storage.list_documents()
            
            # Add raw documents
            raw_documents = file_storage.list_raw_documents()
            documents.extend(raw_documents)
        
        # Apply filters
        filtered_documents = documents
        
        if author:
            filtered_documents = [
                doc for doc in filtered_documents 
                if "author" in doc and doc["author"].lower() == author.lower()
            ]
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered_documents = [
                doc for doc in filtered_documents 
                if (
                    ("title" in doc and keyword_lower in doc["title"].lower()) or
                    ("description" in doc and doc["description"] and keyword_lower in doc["description"].lower()) or
                    ("tags" in doc and doc["tags"] and any(keyword_lower in tag.lower() for tag in doc["tags"]))
                )
            ]
        
        # Sort by modified date (newest first)
        filtered_documents.sort(key=lambda doc: doc.get("modified_at", ""), reverse=True)
        
        # Apply pagination
        paginated_documents = filtered_documents[offset:offset + limit]
        
        # Convert to Document model
        result_documents = []
        for doc in paginated_documents:
            # Create Document model
            document = Document(
                id=doc.get("id", str(uuid.uuid4())),
                title=doc.get("title", "Untitled"),
                description=doc.get("description", ""),
                author=doc.get("author", ""),
                file_path=doc.get("path", ""),
                mimetype=doc.get("mimetype", "application/octet-stream"),
                size=doc.get("size", 0),
                created_at=datetime.fromisoformat(doc.get("created_at", datetime.now().isoformat())),
                modified_at=datetime.fromisoformat(doc.get("modified_at", datetime.now().isoformat())),
                category=doc.get("category", "raw"),
                processed=doc.get("processed", False),
                keywords=doc.get("tags", []),
                pmqa_references=doc.get("pmqa_references", []),
                source=doc.get("source", ""),
                download_url=f"/api/documents/{doc.get('id', '')}/download" if "id" in doc else None
            )
            result_documents.append(document)
        
        return DocumentList(
            total=len(filtered_documents),
            documents=result_documents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str = Path(..., description="Document ID")
):
    """
    Get a specific document by ID.
    
    Args:
        document_id: Document ID
    
    Returns:
        Document details
    """
    try:
        # Look for document in all categories
        all_documents = file_storage.list_documents()
        
        # Add raw documents
        raw_documents = file_storage.list_raw_documents()
        all_documents.extend(raw_documents)
        
        # Find document by ID
        for doc in all_documents:
            if doc.get("id", "") == document_id:
                # Create Document model
                document = Document(
                    id=doc.get("id", document_id),
                    title=doc.get("title", "Untitled"),
                    description=doc.get("description", ""),
                    author=doc.get("author", ""),
                    file_path=doc.get("path", ""),
                    mimetype=doc.get("mimetype", "application/octet-stream"),
                    size=doc.get("size", 0),
                    created_at=datetime.fromisoformat(doc.get("created_at", datetime.now().isoformat())),
                    modified_at=datetime.fromisoformat(doc.get("modified_at", datetime.now().isoformat())),
                    category=doc.get("category", "raw"),
                    processed=doc.get("processed", False),
                    keywords=doc.get("tags", []),
                    pmqa_references=doc.get("pmqa_references", []),
                    source=doc.get("source", ""),
                    download_url=f"/api/documents/{document_id}/download"
                )
                return document
        
        # Document not found
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")


@router.get("/{document_id}/download")
async def download_document(
    document_id: str = Path(..., description="Document ID")
):
    """
    Download a document by ID.
    
    Args:
        document_id: Document ID
    
    Returns:
        File response
    """
    try:
        # Look for document in all categories
        all_documents = file_storage.list_documents()
        
        # Add raw documents
        raw_documents = file_storage.list_raw_documents()
        all_documents.extend(raw_documents)
        
        # Find document by ID
        for doc in all_documents:
            if doc.get("id", "") == document_id:
                file_path = doc.get("path", "")
                filename = os.path.basename(file_path)
                
                # Check if file exists
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail=f"File not found for document {document_id}")
                
                # Return file
                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type=doc.get("mimetype", "application/octet-stream")
                )
        
        # Document not found
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str = Path(..., description="Document ID")
):
    """
    Delete a document by ID.
    
    Args:
        document_id: Document ID
    """
    try:
        # Look for document in all categories
        all_documents = file_storage.list_documents()
        
        # Add raw documents
        raw_documents = file_storage.list_raw_documents()
        all_documents.extend(raw_documents)
        
        # Find document by ID
        for doc in all_documents:
            if doc.get("id", "") == document_id:
                file_path = doc.get("path", "")
                
                # Delete file
                file_storage.delete_document(file_path)
                
                # TODO: Delete from vector and graph databases
                
                return
        
        # Document not found
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_document_processing_status(
    document_id: str = Path(..., description="Document ID")
):
    """
    Get the processing status of a document.
    
    Args:
        document_id: Document ID
    
    Returns:
        Document processing status
    """
    try:
        # Get status from document processor
        status = document_processor.get_processing_status(document_id)
        
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found in processing queue")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document status: {str(e)}")
