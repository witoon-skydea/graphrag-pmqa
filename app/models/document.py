from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class DocumentBase(BaseModel):
    """
    Base model for document information.
    """
    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    author: Optional[str] = Field(None, description="Document author")
    source: Optional[str] = Field(None, description="Document source")
    published_date: Optional[datetime] = Field(None, description="Document publication date")
    category: Optional[str] = Field(None, description="PMQA category (e.g., 'หมวด_1')")
    keywords: Optional[List[str]] = Field(None, description="Document keywords")


class DocumentCreate(DocumentBase):
    """
    Model for creating a new document.
    """
    file_name: str = Field(..., description="Original filename")
    mimetype: str = Field(..., description="MIME type of the document")
    # The actual file content is not included in the model
    # It will be handled by FastAPI's File parameter


class DocumentInDB(DocumentBase):
    """
    Model for document information stored in the database.
    """
    id: str = Field(..., description="Document ID")
    file_path: str = Field(..., description="Path to the document file")
    mimetype: str = Field(..., description="MIME type of the document")
    size: int = Field(..., description="Document size in bytes")
    created_at: datetime = Field(..., description="Document creation timestamp")
    modified_at: datetime = Field(..., description="Document last modified timestamp")
    category: str = Field(..., description="PMQA category (e.g., 'หมวด_1')")
    processed: bool = Field(False, description="Whether the document has been processed")
    pmqa_references: Optional[List[Dict[str, Any]]] = Field(None, description="PMQA structure references")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_123456",
                "title": "รายงานประจำปี 2565",
                "description": "รายงานผลการดำเนินงานประจำปี 2565",
                "author": "กระทรวงสาธารณสุข",
                "source": "กระทรวงสาธารณสุข",
                "published_date": "2022-12-31T00:00:00Z",
                "file_path": "/documents/หมวด_1/รายงานประจำปี_2565.pdf",
                "mimetype": "application/pdf",
                "size": 1234567,
                "created_at": "2023-01-15T10:30:00Z",
                "modified_at": "2023-01-15T10:30:00Z",
                "category": "หมวด_1",
                "processed": True,
                "keywords": ["รายงานประจำปี", "ผลการดำเนินงาน", "กระทรวงสาธารณสุข"],
                "pmqa_references": [
                    {
                        "category_id": "1",
                        "category_name": "การนำองค์การ",
                        "subcategory_id": "1.1",
                        "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง"
                    }
                ]
            }
        }


class Document(DocumentInDB):
    """
    Model for document information returned by the API.
    """
    download_url: Optional[HttpUrl] = Field(None, description="URL to download the document")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "doc_123456",
                "title": "รายงานประจำปี 2565",
                "description": "รายงานผลการดำเนินงานประจำปี 2565",
                "author": "กระทรวงสาธารณสุข",
                "source": "กระทรวงสาธารณสุข",
                "published_date": "2022-12-31T00:00:00Z",
                "file_path": "/documents/หมวด_1/รายงานประจำปี_2565.pdf",
                "mimetype": "application/pdf",
                "size": 1234567,
                "created_at": "2023-01-15T10:30:00Z",
                "modified_at": "2023-01-15T10:30:00Z",
                "category": "หมวด_1",
                "processed": True,
                "keywords": ["รายงานประจำปี", "ผลการดำเนินงาน", "กระทรวงสาธารณสุข"],
                "pmqa_references": [
                    {
                        "category_id": "1",
                        "category_name": "การนำองค์การ",
                        "subcategory_id": "1.1",
                        "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง"
                    }
                ],
                "download_url": "http://example.com/api/documents/doc_123456/download"
            }
        }


class DocumentList(BaseModel):
    """
    Model for a list of documents.
    """
    total: int = Field(..., description="Total number of documents")
    documents: List[Document] = Field(..., description="List of documents")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 2,
                "documents": [
                    {
                        "id": "doc_123456",
                        "title": "รายงานประจำปี 2565",
                        "description": "รายงานผลการดำเนินงานประจำปี 2565",
                        "category": "หมวด_1",
                        "created_at": "2023-01-15T10:30:00Z",
                        "modified_at": "2023-01-15T10:30:00Z",
                        "processed": True
                    },
                    {
                        "id": "doc_789012",
                        "title": "แผนยุทธศาสตร์ 2566-2570",
                        "description": "แผนยุทธศาสตร์การพัฒนาระบบราชการ",
                        "category": "หมวด_2",
                        "created_at": "2023-02-01T14:45:00Z",
                        "modified_at": "2023-02-01T14:45:00Z",
                        "processed": True
                    }
                ]
            }
        }


class DocumentChunk(BaseModel):
    """
    Model for a document chunk.
    """
    id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk content")
    start_idx: int = Field(..., description="Start index in the original document")
    end_idx: int = Field(..., description="End index in the original document")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    vector_id: Optional[str] = Field(None, description="Vector ID in Chroma DB")
    pmqa_references: Optional[List[Dict[str, Any]]] = Field(None, description="PMQA structure references")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "chunk_123456",
                "document_id": "doc_123456",
                "content": "กระทรวงสาธารณสุขได้กำหนดวิสัยทัศน์และพันธกิจดังนี้...",
                "start_idx": 1250,
                "end_idx": 1500,
                "metadata": {
                    "title": "รายงานประจำปี 2565",
                    "category": "หมวด_1",
                    "section": "บทที่ 1"
                },
                "vector_id": "vec_123456",
                "pmqa_references": [
                    {
                        "category_id": "1",
                        "category_name": "การนำองค์การ",
                        "subcategory_id": "1.1",
                        "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง",
                        "criteria_id": "1.1.1",
                        "criteria_name": "การกำหนดทิศทางองค์การที่ชัดเจน"
                    }
                ]
            }
        }


class DocumentProcessingStatus(BaseModel):
    """
    Model for document processing status.
    """
    document_id: str = Field(..., description="Document ID")
    status: str = Field(..., description="Processing status (queued, processing, completed, failed)")
    message: Optional[str] = Field(None, description="Status message")
    start_time: Optional[datetime] = Field(None, description="Processing start time")
    end_time: Optional[datetime] = Field(None, description="Processing end time")
    progress: Optional[float] = Field(None, description="Processing progress (0-100)")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "status": "completed",
                "message": "Document processed successfully",
                "start_time": "2023-01-15T10:30:00Z",
                "end_time": "2023-01-15T10:35:00Z",
                "progress": 100
            }
        }
