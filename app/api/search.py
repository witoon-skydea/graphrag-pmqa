from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Body

from app.models.search import (
    SearchQuery, VectorSearchQuery, GraphSearchQuery, 
    HybridSearchQuery, SearchResults
)
from app.services.graph_rag import graph_rag


router = APIRouter()


@router.post("/", response_model=SearchResults)
async def search(
    query: SearchQuery = Body(..., description="Search query")
):
    """
    Search using the default hybrid search.
    
    Args:
        query: Search query
    
    Returns:
        Search results
    """
    try:
        # Use default hybrid search
        search_results = await graph_rag.search(
            query=query.query,
            search_type="hybrid",
            filters=query.filters
        )
        
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@router.post("/vector", response_model=SearchResults)
async def vector_search(
    query: VectorSearchQuery = Body(..., description="Vector search query")
):
    """
    Search using vector search only.
    
    Args:
        query: Vector search query
    
    Returns:
        Search results
    """
    try:
        # Use vector search
        search_results = await graph_rag.search(
            query=query.query,
            search_type="vector",
            filters=query.filters,
            top_k=query.top_k
        )
        
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing vector search: {str(e)}")


@router.post("/graph", response_model=SearchResults)
async def graph_search(
    query: GraphSearchQuery = Body(..., description="Graph search query")
):
    """
    Search using graph search only.
    
    Args:
        query: Graph search query
    
    Returns:
        Search results
    """
    try:
        # Use graph search
        search_results = await graph_rag.search(
            query=query.query,
            search_type="graph",
            filters=query.filters,
            pmqa_reference=query.pmqa_reference
        )
        
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing graph search: {str(e)}")


@router.post("/hybrid", response_model=SearchResults)
async def hybrid_search(
    query: HybridSearchQuery = Body(..., description="Hybrid search query")
):
    """
    Search using hybrid search with custom weights.
    
    Args:
        query: Hybrid search query
    
    Returns:
        Search results
    """
    try:
        # Validate weights
        if query.vector_weight < 0 or query.vector_weight > 1:
            raise HTTPException(status_code=400, detail="Vector weight must be between 0 and 1")
        if query.graph_weight < 0 or query.graph_weight > 1:
            raise HTTPException(status_code=400, detail="Graph weight must be between 0 and 1")
        if query.vector_weight + query.graph_weight == 0:
            raise HTTPException(status_code=400, detail="At least one weight must be greater than 0")
        
        # Use hybrid search
        search_results = await graph_rag.search(
            query=query.query,
            search_type="hybrid",
            filters=query.filters,
            pmqa_reference=query.pmqa_reference,
            top_k=query.top_k,
            vector_weight=query.vector_weight,
            graph_weight=query.graph_weight
        )
        
        return search_results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing hybrid search: {str(e)}")
