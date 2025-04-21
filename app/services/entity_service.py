from typing import List, Dict, Any, Optional
import requests
import json
import re
from loguru import logger

from app.core.config import settings


class OllamaEntityService:
    """
    Service for analyzing documents using Ollama's LLM to identify PMQA categories,
    extract keywords, and determine relationships.
    """

    def __init__(self):
        """
        Initialize the entity service with configured model.
        """
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.ENTITY_MODEL
        self.generate_url = f"{self.base_url}/api/generate"
        
        # Initialize PMQA structure
        self.pmqa_structure = self._load_pmqa_structure()
    
    def _load_pmqa_structure(self) -> Dict[str, Any]:
        """
        Load PMQA structure from file.
        
        Returns:
            Dictionary containing PMQA structure
        """
        try:
            with open(settings.PMQA_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading PMQA structure: {str(e)}")
            # Return minimal structure
            return {
                "categories": [
                    {"id": str(i), "name": f"หมวด {i}", "description": ""} 
                    for i in range(1, 8)
                ]
            }

    def analyze_document(
        self, 
        text: str, 
        document_id: str
    ) -> Dict[str, Any]:
        """
        Analyze document content to identify PMQA categories, extract keywords, etc.
        
        Args:
            text: Document text
            document_id: Document ID
            
        Returns:
            Analysis results including PMQA references, keywords, etc.
        """
        try:
            # Extract a summary or sample for analysis if text is too long
            sample_text = self._extract_sample(text)
            
            # Create a prompt for the LLM
            prompt = self._create_analysis_prompt(sample_text)
            
            # Send request to Ollama
            result = self._query_llm(prompt)
            
            # Parse the result
            analysis = self._parse_analysis_result(result)
            
            logger.info(f"Document {document_id} analyzed: found {len(analysis.get('pmqa_references', []))} PMQA references")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing document {document_id}: {str(e)}")
            # Return minimal analysis
            return {
                "pmqa_references": [],
                "keywords": [],
                "entities": []
            }

    def _extract_sample(self, text: str, max_length: int = 5000) -> str:
        """
        Extract a representative sample from text if it's too long.
        
        Args:
            text: Input text
            max_length: Maximum sample length
            
        Returns:
            Text sample
        """
        if len(text) <= max_length:
            return text
        
        # Take beginning, middle, and end sections
        third = max_length // 3
        beginning = text[:third]
        middle_start = (len(text) - third) // 2
        middle = text[middle_start:middle_start + third]
        end = text[-third:]
        
        return f"{beginning}\n\n[...]\n\n{middle}\n\n[...]\n\n{end}"

    def _create_analysis_prompt(self, text: str) -> str:
        """
        Create a prompt for the LLM to analyze the document.
        
        Args:
            text: Document text
            
        Returns:
            Prompt for the LLM
        """
        return f"""
คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์เอกสารตามเกณฑ์ PMQA 4.0 (Public Sector Management Quality Award)

PMQA 4.0 แบ่งออกเป็น 7 หมวด ดังนี้:
หมวด 1: การนำองค์การ
หมวด 2: การวางแผนเชิงยุทธศาสตร์
หมวด 3: การให้ความสำคัญกับผู้รับบริการและผู้มีส่วนได้ส่วนเสีย
หมวด 4: การวัด การวิเคราะห์ และการจัดการความรู้
หมวด 5: การมุ่งเน้นบุคลากร
หมวด 6: การมุ่งเน้นระบบปฏิบัติการ
หมวด 7: ผลลัพธ์การดำเนินการ

กรุณาวิเคราะห์เอกสารต่อไปนี้และให้ข้อมูลในรูปแบบ JSON:
1. pmqa_references: รายการอ้างอิงถึงหมวด PMQA ที่เกี่ยวข้อง ระบุ category_id, category_name
2. keywords: คำสำคัญที่พบในเอกสาร
3. summary: สรุปเนื้อหาสำคัญของเอกสาร

เอกสาร:
```
{text}
```

แสดงผลลัพธ์เป็น JSON:
"""

    def _query_llm(self, prompt: str) -> str:
        """
        Send a query to the LLM using Ollama API.
        
        Args:
            prompt: LLM prompt
            
        Returns:
            LLM response
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,  # Low temperature for more deterministic results
                "system": "You are an expert document analyst specializing in PMQA 4.0 framework analysis."
            }
            
            response = requests.post(self.generate_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Error querying LLM: {str(e)}")
            raise

    def _parse_analysis_result(self, result: str) -> Dict[str, Any]:
        """
        Parse the analysis result from the LLM.
        
        Args:
            result: LLM response
            
        Returns:
            Parsed analysis
        """
        try:
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = result
                
            # Remove any markdown formatting
            json_str = re.sub(r'```.*?```', '', json_str, flags=re.DOTALL)
            
            # Clean up JSON
            json_str = json_str.strip()
            json_str = re.sub(r'^```|```$', '', json_str)
            
            analysis = json.loads(json_str)
            
            # Ensure required fields exist
            if "pmqa_references" not in analysis:
                analysis["pmqa_references"] = []
            if "keywords" not in analysis:
                analysis["keywords"] = []
                
            return analysis
        except Exception as e:
            logger.error(f"Error parsing analysis result: {str(e)}")
            # Return empty analysis as fallback
            return {
                "pmqa_references": [],
                "keywords": [],
                "summary": "Could not analyze document."
            }


# Alternative implementation using a mock service for testing
class MockEntityService:
    """
    Mock entity service for testing purposes.
    """

    def __init__(self):
        """
        Initialize the mock entity service.
        """
        logger.warning("Using mock entity service - not suitable for production")
        
        # Initialize mock PMQA structure
        self.pmqa_categories = [
            {"id": "1", "name": "การนำองค์การ"},
            {"id": "2", "name": "การวางแผนเชิงยุทธศาสตร์"},
            {"id": "3", "name": "การให้ความสำคัญกับผู้รับบริการและผู้มีส่วนได้ส่วนเสีย"},
            {"id": "4", "name": "การวัด การวิเคราะห์ และการจัดการความรู้"},
            {"id": "5", "name": "การมุ่งเน้นบุคลากร"},
            {"id": "6", "name": "การมุ่งเน้นระบบปฏิบัติการ"},
            {"id": "7", "name": "ผลลัพธ์การดำเนินการ"}
        ]

    def analyze_document(
        self, 
        text: str, 
        document_id: str
    ) -> Dict[str, Any]:
        """
        Analyze document content with mock implementation.
        
        Args:
            text: Document text
            document_id: Document ID
            
        Returns:
            Mock analysis results
        """
        # Simple keyword-based analysis
        pmqa_references = []
        keywords = []
        
        # Check for keywords related to each PMQA category
        keyword_map = {
            "1": ["ผู้บริหาร", "วิสัยทัศน์", "พันธกิจ", "ค่านิยม", "นำองค์การ", "ธรรมาภิบาล"],
            "2": ["ยุทธศาสตร์", "แผน", "กลยุทธ์", "เป้าหมาย", "วัตถุประสงค์", "ตัวชี้วัด"],
            "3": ["ผู้รับบริการ", "ลูกค้า", "ประชาชน", "ผู้มีส่วนได้ส่วนเสีย", "ความพึงพอใจ"],
            "4": ["ข้อมูล", "สารสนเทศ", "ความรู้", "วิเคราะห์", "ตัดสินใจ", "เทคโนโลยี"],
            "5": ["บุคลากร", "พนักงาน", "การพัฒนา", "การฝึกอบรม", "สวัสดิการ", "ความผูกพัน"],
            "6": ["กระบวนการ", "ปฏิบัติการ", "นวัตกรรม", "ประสิทธิภาพ", "มาตรฐาน"],
            "7": ["ผลลัพธ์", "ผลการดำเนินงาน", "ตัวชี้วัด", "ประสิทธิผล", "เปรียบเทียบ"]
        }
        
        # Extract sample text
        sample_text = text[:10000].lower()
        
        # Find references to PMQA categories
        for category in self.pmqa_categories:
            category_id = category["id"]
            
            # Check if any keywords for this category appear in the text
            for keyword in keyword_map.get(category_id, []):
                if keyword.lower() in sample_text:
                    pmqa_references.append({
                        "category_id": category_id,
                        "category_name": category["name"]
                    })
                    keywords.append(keyword)
                    break
        
        # Ensure at least one category is selected
        if not pmqa_references:
            # Default to category 1
            pmqa_references.append({
                "category_id": "1",
                "category_name": "การนำองค์การ"
            })
        
        # Create mock summary
        summary = f"เอกสารนี้เกี่ยวข้องกับ {', '.join([ref['category_name'] for ref in pmqa_references])}"
        
        return {
            "pmqa_references": pmqa_references,
            "keywords": list(set(keywords)),  # Deduplicate keywords
            "summary": summary
        }


# Choose the actual implementation based on availability of Ollama
try:
    # Test if Ollama is available
    requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
    entity_service = OllamaEntityService()
    logger.info(f"Using Ollama entity service with model {settings.ENTITY_MODEL}")
except Exception as e:
    logger.warning(f"Ollama service not available, using mock entity service: {str(e)}")
    entity_service = MockEntityService()
