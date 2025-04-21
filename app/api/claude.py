from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body

from app.models.search import ClaudeQuery, ClaudeResponse
from app.services.claude_service import claude_service


router = APIRouter()


@router.post("/query", response_model=ClaudeResponse)
async def ask_claude(
    query: ClaudeQuery = Body(..., description="Query for Claude AI")
):
    """
    Send a question to Claude AI, optionally using retrieval-augmented generation.
    
    Args:
        query: Query for Claude
    
    Returns:
        Response from Claude AI
    """
    try:
        # Send query to Claude service
        response = await claude_service.answer_question(
            query=query.query,
            use_rag=query.use_rag,
            search_type=query.search_type,
            pmqa_reference=query.pmqa_reference,
            max_tokens=query.max_tokens or 1000
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Claude AI: {str(e)}")
