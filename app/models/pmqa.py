from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Criteria(BaseModel):
    """
    Model for PMQA criteria.
    """
    id: str = Field(..., description="Criteria ID (e.g., '1.1.1')")
    name: str = Field(..., description="Criteria name")
    description: Optional[str] = Field(None, description="Criteria description")
    subcategory_id: str = Field(..., description="Parent subcategory ID")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "1.1.1",
                "name": "การกำหนดทิศทางองค์การที่ชัดเจน",
                "description": "การกำหนดวิสัยทัศน์ พันธกิจ ค่านิยมหลัก และทิศทางเชิงยุทธศาสตร์ขององค์การ",
                "subcategory_id": "1.1"
            }
        }


class Subcategory(BaseModel):
    """
    Model for PMQA subcategory.
    """
    id: str = Field(..., description="Subcategory ID (e.g., '1.1')")
    name: str = Field(..., description="Subcategory name")
    description: Optional[str] = Field(None, description="Subcategory description")
    category_id: str = Field(..., description="Parent category ID")
    criteria: Optional[List[Criteria]] = Field(None, description="List of criteria in this subcategory")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "1.1",
                "name": "การนำองค์การ",
                "description": "การกำหนดทิศทางองค์การโดยผู้บริหารระดับสูง",
                "category_id": "1",
                "criteria": [
                    {
                        "id": "1.1.1",
                        "name": "การกำหนดทิศทางองค์การที่ชัดเจน",
                        "description": "...",
                        "subcategory_id": "1.1"
                    }
                ]
            }
        }


class Category(BaseModel):
    """
    Model for PMQA category.
    """
    id: str = Field(..., description="Category ID (e.g., '1')")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    subcategories: Optional[List[Subcategory]] = Field(None, description="List of subcategories in this category")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "1",
                "name": "การนำองค์การ",
                "description": "การนำองค์การโดยผู้บริหารระดับสูง",
                "subcategories": [
                    {
                        "id": "1.1",
                        "name": "การนำองค์การ",
                        "description": "...",
                        "category_id": "1",
                        "criteria": []
                    }
                ]
            }
        }


class PMQAStructure(BaseModel):
    """
    Model for the complete PMQA structure.
    """
    categories: List[Category] = Field(..., description="List of PMQA categories")
    
    class Config:
        schema_extra = {
            "example": {
                "categories": [
                    {
                        "id": "1",
                        "name": "การนำองค์การ",
                        "description": "...",
                        "subcategories": []
                    },
                    {
                        "id": "2",
                        "name": "การวางแผนเชิงยุทธศาสตร์",
                        "description": "...",
                        "subcategories": []
                    }
                ]
            }
        }


class PMQAReference(BaseModel):
    """
    Model for referencing PMQA categories, subcategories, or criteria.
    """
    category_id: Optional[str] = Field(None, description="Category ID")
    category_name: Optional[str] = Field(None, description="Category name")
    subcategory_id: Optional[str] = Field(None, description="Subcategory ID")
    subcategory_name: Optional[str] = Field(None, description="Subcategory name")
    criteria_id: Optional[str] = Field(None, description="Criteria ID")
    criteria_name: Optional[str] = Field(None, description="Criteria name")
    
    class Config:
        schema_extra = {
            "example": {
                "category_id": "1",
                "category_name": "การนำองค์การ",
                "subcategory_id": "1.1",
                "subcategory_name": "การนำองค์การโดยผู้บริหารระดับสูง",
                "criteria_id": "1.1.1",
                "criteria_name": "การกำหนดทิศทางองค์การที่ชัดเจน"
            }
        }
