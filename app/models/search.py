from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """
    Base model for search queries.
    """
    query: str = Field(..., description="Search query text")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters for search")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "การกำหนดวิสัยทัศน์และพันธกิจของกระทรวงสาธารณสุข",
                "filters": {
                    "category": "หมวด_1",
                    "published_after": "2022-01-01"
                }
            }
        }


class VectorSearchQuery(SearchQuery):
    """
    Model for vector search queries.
    """
    top_k: int = Field(5, description="Number of top results to return")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "การกำหนดวิสัยทัศน์และพันธกิจของกระทรวงสาธารณสุข",
                "filters": {
                    "category": "หมวด_1",
                    "published_after": "2022-01-01"
                },
                "top_k": 5
            }
        }


class GraphSearchQuery(SearchQuery):
    """
    Model for graph search queries.
    """
    pmqa_reference: Optional[Dict[str, str]] = Field(None, description="PMQA reference to search within")
    max_hops: int = Field(2, description="Maximum number of hops in the graph")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "การกำหนดวิสัยทัศน์และพันธกิจของกระทรวงสาธารณสุข",
                "filters": {
                    "published_after": "2022-01-01"
                },
                "pmqa_reference": {
                    "category_id": "1",
                    "subcategory_id": "1.1"
                },
                "max_hops": 2
            }
        }


class HybridSearchQuery(SearchQuery):
    """
    Model for hybrid search queries (combining vector and graph search).
    """
    vector_weight: float = Field(0.5, description="Weight for vector search results (0-1)")
    graph_weight: float = Field(0.5, description="Weight for graph search results (0-1)")
    pmqa_reference: Optional[Dict[str, str]] = Field(None, description="PMQA reference to search within")
    top_k: int = Field(10, description="Number of top results to return")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "การกำหนดวิสัยทัศน์และพันธกิจของกระทรวงสาธารณสุข",
                "filters": {
                    "published_after": "2022-01-01"
                },
                "pmqa_reference": {
                    "category_id": "1",
                    "subcategory_id": "1.1"
                },
                "vector_weight": 0.7,
                "graph_weight": 0.3,
                "top_k": 10
            }
        }


class SearchResult(BaseModel):
    """
    Model for a single search result.
    """
    document_id: str = Field(..., description="Document ID")
    document_title: str = Field(..., description="Document title")
    chunk_id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., description="Search result score")
    pmqa_references: List[Dict[str, str]] = Field(..., description="PMQA references")
    metadata: Dict[str, Any] = Field(..., description="Result metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "document_title": "รายงานประจำปี 2565",
                "chunk_id": "chunk_789012",
                "content": "กระทรวงสาธารณสุขได้กำหนดวิสัยทัศน์คือ 'เป็นองค์กรหลักด้านสุขภาพ ที่รวมพลังสังคม เพื่อประชาชนสุขภาพดี' และมีพันธกิจในการ...",
                "score": 0.92,
                "pmqa_references": [
                    {
                        "category_id": "1",
                        "category_name": "การนำองค์การ",
                        "subcategory_id": "1.1",
                        "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง",
                        "criteria_id": "1.1.1",
                        "criteria_name": "การกำหนดทิศทางองค์การที่ชัดเจน"
                    }
                ],
                "metadata": {
                    "published_date": "2022-12-31",
                    "author": "กระทรวงสาธารณสุข",
                    "source": "กระทรวงสาธารณสุข",
                    "document_url": "/api/documents/doc_123456"
                }
            }
        }


class SearchResults(BaseModel):
    """
    Model for search results.
    """
    query: str = Field(..., description="Original query string")
    total_results: int = Field(..., description="Total number of results")
    results: List[SearchResult] = Field(..., description="Search results")
    search_type: str = Field(..., description="Type of search performed (vector, graph, hybrid)")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "การกำหนดวิสัยทัศน์และพันธกิจของกระทรวงสาธารณสุข",
                "total_results": 3,
                "results": [
                    {
                        "document_id": "doc_123456",
                        "document_title": "รายงานประจำปี 2565",
                        "chunk_id": "chunk_789012",
                        "content": "กระทรวงสาธารณสุขได้กำหนดวิสัยทัศน์คือ 'เป็นองค์กรหลักด้านสุขภาพ ที่รวมพลังสังคม เพื่อประชาชนสุขภาพดี' และมีพันธกิจในการ...",
                        "score": 0.92,
                        "pmqa_references": [
                            {
                                "category_id": "1",
                                "category_name": "การนำองค์การ",
                                "subcategory_id": "1.1",
                                "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง"
                            }
                        ],
                        "metadata": {
                            "published_date": "2022-12-31",
                            "author": "กระทรวงสาธารณสุข"
                        }
                    }
                ],
                "search_type": "hybrid",
                "execution_time_ms": 156.32
            }
        }


class ClaudeQuery(BaseModel):
    """
    Model for queries to Claude AI.
    """
    query: str = Field(..., description="Question to ask Claude AI")
    use_rag: bool = Field(True, description="Whether to use RAG for context")
    search_type: str = Field("hybrid", description="Type of search to use for RAG")
    pmqa_reference: Optional[Dict[str, str]] = Field(None, description="PMQA reference to search within")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens in the response")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "วิสัยทัศน์ของกระทรวงสาธารณสุขคืออะไร และมีการถ่ายทอดวิสัยทัศน์สู่การปฏิบัติอย่างไร?",
                "use_rag": True,
                "search_type": "hybrid",
                "pmqa_reference": {
                    "category_id": "1",
                    "subcategory_id": "1.1"
                },
                "max_tokens": 1000
            }
        }


class ClaudeResponse(BaseModel):
    """
    Model for responses from Claude AI.
    """
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Answer from Claude AI")
    sources: List[Dict[str, Any]] = Field(..., description="Sources used to generate the answer")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "วิสัยทัศน์ของกระทรวงสาธารณสุขคืออะไร และมีการถ่ายทอดวิสัยทัศน์สู่การปฏิบัติอย่างไร?",
                "answer": "วิสัยทัศน์ของกระทรวงสาธารณสุขคือ 'เป็นองค์กรหลักด้านสุขภาพ ที่รวมพลังสังคม เพื่อประชาชนสุขภาพดี' \n\nการถ่ายทอดวิสัยทัศน์สู่การปฏิบัติ ดำเนินการผ่านกระบวนการสำคัญดังนี้...",
                "sources": [
                    {
                        "document_id": "doc_123456",
                        "document_title": "รายงานประจำปี 2565",
                        "chunk_id": "chunk_789012",
                        "content_snippet": "กระทรวงสาธารณสุขได้กำหนดวิสัยทัศน์คือ 'เป็นองค์กรหลักด้านสุขภาพ ที่รวมพลังสังคม เพื่อประชาชนสุขภาพดี'",
                        "relevance_score": 0.95
                    }
                ],
                "execution_time_ms": 2345.67
            }
        }
