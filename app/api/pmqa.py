from typing import Dict, Any
import json
from fastapi import APIRouter, HTTPException
from loguru import logger

from app.core.config import settings
from app.models.pmqa import PMQAStructure


router = APIRouter()


@router.get("/structure", response_model=PMQAStructure)
async def get_pmqa_structure():
    """
    Get the PMQA 4.0 structure.
    
    Returns:
        PMQA structure
    """
    try:
        # Load PMQA structure from file
        with open(settings.PMQA_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
            pmqa_data = json.load(f)
        
        return pmqa_data
    except FileNotFoundError:
        # Create a minimal structure if file doesn't exist
        logger.warning(f"PMQA structure file not found at {settings.PMQA_STRUCTURE_FILE}, returning minimal structure")
        
        minimal_structure = {
            "categories": [
                {
                    "id": str(i),
                    "name": f"หมวด {i}",
                    "description": f"PMQA 4.0 หมวดที่ {i}",
                    "subcategories": []
                } 
                for i in range(1, 8)
            ]
        }
        
        return minimal_structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting PMQA structure: {str(e)}")
