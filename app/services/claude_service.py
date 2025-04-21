from typing import List, Dict, Any, Optional
import requests
import json
import time
from loguru import logger

from app.core.config import settings
from app.services.graph_rag import graph_rag


class ClaudeService:
    """
    Service for interacting with Claude AI API to answer questions based on RAG results.
    """

    def __init__(self):
        """
        Initialize the Claude service.
        """
        self.api_key = settings.CLAUDE_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key
        }

    async def answer_question(
        self, 
        query: str, 
        use_rag: bool = True,
        search_type: str = "hybrid",
        pmqa_reference: Optional[Dict[str, str]] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Answer a question using Claude API, optionally with RAG context.
        
        Args:
            query: User's question
            use_rag: Whether to use RAG for context
            search_type: Type of search for RAG ("vector", "graph", or "hybrid")
            pmqa_reference: Optional PMQA reference to focus the search
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Answer from Claude AI and sources used
        """
        try:
            start_time = time.time()
            
            # If using RAG, get relevant context
            context = ""
            sources = []
            
            if use_rag:
                # Get RAG results
                rag_results = await graph_rag.search(
                    query=query,
                    search_type=search_type,
                    pmqa_reference=pmqa_reference,
                    top_k=5  # Limit to top 5 results for context
                )
                
                # Extract context from results
                sources = rag_results.get("results", [])
                context = self._prepare_context(sources)
            
            # Create prompt for Claude
            prompt = self._create_prompt(query, context)
            
            # Call Claude API
            response = await self._call_claude_api(prompt, max_tokens)
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            return {
                "query": query,
                "answer": response,
                "sources": sources,
                "execution_time_ms": execution_time_ms
            }
        except Exception as e:
            logger.error(f"Error in Claude service: {str(e)}")
            raise

    def _prepare_context(self, sources: List[Dict[str, Any]]) -> str:
        """
        Prepare context from RAG results.
        
        Args:
            sources: List of RAG results
            
        Returns:
            Formatted context string
        """
        if not sources:
            return ""
        
        context_parts = ["### ข้อมูลอ้างอิง ###\n"]
        
        for i, source in enumerate(sources, 1):
            source_text = f"[{i}] จากเอกสาร: {source.get('document_title', 'ไม่ระบุ')}\n"
            source_text += f"เนื้อหา: {source.get('content', '')}\n"
            
            # Add PMQA references if available
            pmqa_refs = source.get("pmqa_references", [])
            if pmqa_refs:
                refs_text = ", ".join([
                    f"{ref.get('category_name', '')} ({ref.get('category_id', '')})"
                    for ref in pmqa_refs
                ])
                source_text += f"เกี่ยวข้องกับ PMQA: {refs_text}\n"
                
            context_parts.append(source_text)
            
        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for Claude.
        
        Args:
            query: User's question
            context: Context from RAG
            
        Returns:
            Prompt for Claude API
        """
        if context:
            return f"""คุณเป็นผู้เชี่ยวชาญในการตอบคำถามเกี่ยวกับ PMQA 4.0 (Public Sector Management Quality Award)

ฉันจะให้ข้อมูลอ้างอิงที่เกี่ยวข้องสำหรับการตอบคำถาม ให้ใช้ข้อมูลนี้ในการตอบ และอ้างอิงแหล่งที่มาของข้อมูลโดยใช้หมายเลขในวงเล็บเช่น [1], [2], ฯลฯ

{context}

### คำถาม ###
{query}

### คำตอบ ###
"""
        else:
            return f"""คุณเป็นผู้เชี่ยวชาญในการตอบคำถามเกี่ยวกับ PMQA 4.0 (Public Sector Management Quality Award)

### คำถาม ###
{query}

### คำตอบ ###
"""

    async def _call_claude_api(self, prompt: str, max_tokens: int) -> str:
        """
        Call Claude API with a prompt.
        
        Args:
            prompt: Prompt for Claude
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Claude's response
        """
        # Check if API key is configured
        if not self.api_key or self.api_key == "":
            logger.warning("Claude API key not configured, using mock response")
            return self._generate_mock_response(prompt)
        
        try:
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("content", [{}])[0].get("text", "ไม่สามารถรับข้อมูลจาก Claude AI ได้")
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return f"ขออภัย ไม่สามารถเชื่อมต่อกับ Claude AI ได้ในขณะนี้ (ข้อผิดพลาด: {str(e)})"

    def _generate_mock_response(self, prompt: str) -> str:
        """
        Generate a mock response for testing purposes.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        # Extract query from prompt
        query_match = prompt.split("### คำถาม ###")
        if len(query_match) > 1:
            query_part = query_match[1].split("### คำตอบ ###")[0].strip()
        else:
            query_part = prompt
            
        # Generate simple mock response
        if "วิสัยทัศน์" in query_part.lower():
            return """วิสัยทัศน์ของ PMQA 4.0 คือการพัฒนาองค์การภาครัฐให้มีคุณภาพและมาตรฐานเทียบเท่าสากล โดยมุ่งเน้นการพัฒนาองค์การให้มีขีดสมรรถนะสูงและทันสมัย บุคลากรมีความเป็นมืออาชีพ และระบบราชการต้องเป็นที่พึ่งของประชาชนและเป็นที่เชื่อถือไว้วางใจได้ [1]

PMQA 4.0 ได้กำหนดเป้าหมายการพัฒนาคุณภาพการบริหารจัดการภาครัฐที่มุ่งสู่การเป็นระบบราชการ 4.0 ที่มีลักษณะสำคัญ 3 ประการ ได้แก่ [2]
1. เปิดกว้างและเชื่อมโยงกัน
2. ยึดประชาชนเป็นศูนย์กลาง
3. มีขีดสมรรถนะสูงและทันสมัย"""
        elif "หมวด" in query_part.lower():
            return """PMQA 4.0 แบ่งออกเป็น 7 หมวด ดังนี้ [1]:

1. หมวด 1: การนำองค์การ - เน้นบทบาทของผู้บริหารในการกำหนดทิศทางองค์การ สร้างบรรยากาศที่ส่งเสริมการบรรลุพันธกิจและวิสัยทัศน์

2. หมวด 2: การวางแผนเชิงยุทธศาสตร์ - การจัดทำแผนยุทธศาสตร์ วัตถุประสงค์เชิงยุทธศาสตร์ และกลยุทธ์หลัก รวมทั้งการถ่ายทอดไปสู่การปฏิบัติ

3. หมวด 3: การให้ความสำคัญกับผู้รับบริการและผู้มีส่วนได้ส่วนเสีย - การเรียนรู้ความต้องการและความคาดหวัง การสร้างความสัมพันธ์และความพึงพอใจ

4. หมวด 4: การวัด การวิเคราะห์ และการจัดการความรู้ - การจัดการระบบสารสนเทศ การวัดผลการดำเนินการ และการจัดการความรู้

5. หมวด 5: การมุ่งเน้นบุคลากร - ระบบงาน การพัฒนาบุคลากร และการสร้างความผูกพัน

6. หมวด 6: การมุ่งเน้นระบบปฏิบัติการ - การออกแบบและจัดการกระบวนการ การสร้างนวัตกรรม และการเตรียมพร้อมต่อเหตุฉุกเฉิน

7. หมวด 7: ผลลัพธ์การดำเนินการ - ผลลัพธ์ด้านประสิทธิผล การให้บริการ การมุ่งเน้นลูกค้า บุคลากร การนำองค์การ และงบประมาณ [2]

แต่ละหมวดมีความเชื่อมโยงกัน โดยมีหมวด 1 เป็นหมวดนำที่กำหนดทิศทาง และหมวด 7 เป็นหมวดผลลัพธ์ ส่วนหมวด 2-6 เป็นหมวดกระบวนการที่สนับสนุนการบรรลุผลลัพธ์ [1]"""
        else:
            return """ขออภัย ฉันไม่มีข้อมูลเฉพาะเจาะจงเกี่ยวกับคำถามนี้ในแหล่งข้อมูลที่ได้รับ

ในการตอบคำถามเกี่ยวกับ PMQA 4.0 อย่างถูกต้อง ควรอ้างอิงจากเกณฑ์ PMQA 4.0 ฉบับล่าสุดที่จัดทำโดยสำนักงานคณะกรรมการพัฒนาระบบราชการ (ก.พ.ร.) 

หากต้องการข้อมูลเพิ่มเติม แนะนำให้ศึกษาจากคู่มือการประเมิน PMQA 4.0 หรือติดต่อเจ้าหน้าที่ผู้รับผิดชอบงานพัฒนาระบบราชการในหน่วยงานของท่าน"""


# Create a singleton instance
claude_service = ClaudeService()
