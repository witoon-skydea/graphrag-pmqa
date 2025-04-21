import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
import asyncio
from io import BytesIO

# Import service ที่จะทดสอบ (ให้แก้ import path ตามโครงสร้างโปรเจคจริง)
# from app.services.document_service import DocumentService

# Mock ของ DocumentService สำหรับการทดสอบ
class MockDocumentService:
    async def upload_document(self, file, filename, category, subcategory):
        return "doc123"
    
    async def get_document(self, document_id):
        if document_id == "doc123":
            return {
                "id": "doc123",
                "filename": "test.pdf",
                "category": "หมวด_1",
                "subcategory": "1.1",
                "content": "Test content",
                "status": "processed"
            }
        return None
    
    async def get_document_chunks(self, document_id):
        if document_id == "doc123":
            return [
                {"id": "chunk1", "content": "Test content chunk 1", "document_id": "doc123"},
                {"id": "chunk2", "content": "Test content chunk 2", "document_id": "doc123"}
            ]
        return []
    
    async def delete_document(self, document_id):
        return True if document_id == "doc123" else False
    
    async def get_documents_by_category(self, category):
        if category == "หมวด_1":
            return [
                {"id": "doc123", "filename": "test.pdf", "category": "หมวด_1"},
                {"id": "doc456", "filename": "test2.pdf", "category": "หมวด_1"}
            ]
        return []

# การทดสอบหน่วยสำหรับ DocumentService
@pytest.mark.unit
class TestDocumentService:
    
    @pytest.fixture
    def document_service(self):
        """สร้าง instance ของ DocumentService สำหรับการทดสอบ"""
        # สำหรับการทดสอบจริง ให้สร้าง instance ของ DocumentService จริงๆ
        # return DocumentService()
        
        # สำหรับตัวอย่างนี้ ใช้ Mock แทน
        return MockDocumentService()
    
    @pytest.mark.asyncio
    async def test_upload_document(self, document_service, temp_document_dir):
        """ทดสอบการอัปโหลดเอกสาร"""
        # สร้างไฟล์ทดสอบ
        test_file = BytesIO(b"%PDF-1.4\nTest PMQA document content")
        
        # ทดสอบการอัปโหลดเอกสาร
        document_id = await document_service.upload_document(
            file=test_file,
            filename="test.pdf",
            category="หมวด_1",
            subcategory="1.1"
        )
        
        # ตรวจสอบว่าได้รับ document_id กลับมา
        assert document_id == "doc123"
    
    @pytest.mark.asyncio
    async def test_get_document(self, document_service):
        """ทดสอบการดึงข้อมูลเอกสาร"""
        # ทดสอบการดึงข้อมูลเอกสารที่มีอยู่
        document = await document_service.get_document("doc123")
        
        # ตรวจสอบผลลัพธ์
        assert document is not None
        assert document["id"] == "doc123"
        assert document["filename"] == "test.pdf"
        assert document["category"] == "หมวด_1"
        assert document["subcategory"] == "1.1"
        assert document["status"] == "processed"
        
        # ทดสอบการดึงข้อมูลเอกสารที่ไม่มีอยู่
        document = await document_service.get_document("non_existent_id")
        assert document is None
    
    @pytest.mark.asyncio
    async def test_get_document_chunks(self, document_service):
        """ทดสอบการดึงข้อมูล chunks ของเอกสาร"""
        # ทดสอบการดึงข้อมูล chunks ของเอกสารที่มีอยู่
        chunks = await document_service.get_document_chunks("doc123")
        
        # ตรวจสอบผลลัพธ์
        assert len(chunks) == 2
        assert chunks[0]["id"] == "chunk1"
        assert chunks[0]["document_id"] == "doc123"
        assert chunks[1]["id"] == "chunk2"
        
        # ทดสอบการดึงข้อมูล chunks ของเอกสารที่ไม่มีอยู่
        chunks = await document_service.get_document_chunks("non_existent_id")
        assert len(chunks) == 0
    
    @pytest.mark.asyncio
    async def test_delete_document(self, document_service):
        """ทดสอบการลบเอกสาร"""
        # ทดสอบการลบเอกสารที่มีอยู่
        result = await document_service.delete_document("doc123")
        assert result is True
        
        # ทดสอบการลบเอกสารที่ไม่มีอยู่
        result = await document_service.delete_document("non_existent_id")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_documents_by_category(self, document_service):
        """ทดสอบการดึงข้อมูลเอกสารตามหมวดหมู่"""
        # ทดสอบการดึงข้อมูลเอกสารตามหมวดหมู่ที่มีเอกสาร
        documents = await document_service.get_documents_by_category("หมวด_1")
        
        # ตรวจสอบผลลัพธ์
        assert len(documents) == 2
        assert documents[0]["id"] == "doc123"
        assert documents[0]["category"] == "หมวด_1"
        assert documents[1]["id"] == "doc456"
        
        # ทดสอบการดึงข้อมูลเอกสารตามหมวดหมู่ที่ไม่มีเอกสาร
        documents = await document_service.get_documents_by_category("หมวด_99")
        assert len(documents) == 0

# การรันการทดสอบแบบ standalone (ไม่ผ่าน pytest)
if __name__ == "__main__":
    # สร้าง mock event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # สร้าง DocumentService
    service = MockDocumentService()
    
    # ทดสอบ get_document
    result = loop.run_until_complete(service.get_document("doc123"))
    print(f"Get Document Result: {result}")
    
    # ทดสอบ get_document_chunks
    chunks = loop.run_until_complete(service.get_document_chunks("doc123"))
    print(f"Get Document Chunks Result: {len(chunks)} chunks")
    
    # ปิด event loop
    loop.close()