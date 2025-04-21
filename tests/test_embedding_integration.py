import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
import numpy as np

# Import services ที่จะทดสอบ (ให้แก้ import path ตามโครงสร้างโปรเจคจริง)
# from app.services.document_service import DocumentService
# from app.services.embedding_service import EmbeddingService
# from app.services.entity_service import EntityService
# from app.db.vector_db import vector_db

# Mock ของ EmbeddingService สำหรับการทดสอบ
class MockEmbeddingService:
    async def create_embedding(self, text):
        # สร้าง vector จำลองขนาด 384 มิติ (ขนาดเดียวกับ nomic-embed-text)
        return np.random.rand(384).tolist()
    
    async def get_embedding(self, chunk_id):
        # สร้าง vector จำลองขนาด 384 มิติ
        return np.random.rand(384).tolist()
    
    async def create_embeddings_for_document(self, document_id, chunks):
        # จำลองการสร้าง embeddings สำหรับทุก chunk
        return [{"id": chunk["id"], "embedding": np.random.rand(384).tolist()} for chunk in chunks]

# Mock ของ DocumentService สำหรับการทดสอบ
class MockDocumentService:
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

# Mock ของ VectorDB สำหรับการทดสอบ
class MockVectorDB:
    def __init__(self):
        self.collections = {}
        self.client = MagicMock()
        self.client.list_collections.return_value = []
    
    def get_or_create_collection(self, name):
        if name not in self.collections:
            mock_collection = MagicMock()
            mock_collection.name = name
            self.collections[name] = mock_collection
        return self.collections[name]

# การทดสอบการทำงานร่วมกันสำหรับกระบวนการ Embedding
@pytest.mark.integration
class TestEmbeddingIntegration:
    
    @pytest.fixture
    def embedding_service(self):
        """สร้าง instance ของ EmbeddingService สำหรับการทดสอบ"""
        # สำหรับการทดสอบจริง ให้สร้าง instance ของ EmbeddingService จริงๆ
        # return EmbeddingService()
        
        # สำหรับตัวอย่างนี้ ใช้ Mock แทน
        return MockEmbeddingService()
    
    @pytest.fixture
    def document_service(self):
        """สร้าง instance ของ DocumentService สำหรับการทดสอบ"""
        # สำหรับการทดสอบจริง ให้สร้าง instance ของ DocumentService จริงๆ
        # return DocumentService()
        
        # สำหรับตัวอย่างนี้ ใช้ Mock แทน
        return MockDocumentService()
    
    @pytest.fixture
    def mock_vector_db(self):
        """สร้าง mock ของ VectorDB สำหรับการทดสอบ"""
        with patch("app.db.vector_db.vector_db", MockVectorDB()):
            yield
    
    @pytest.mark.asyncio
    async def test_embedding_creation_flow(self, embedding_service, document_service, mock_vector_db):
        """ทดสอบกระบวนการสร้าง Embedding แบบครบวงจร"""
        # ดึงข้อมูลเอกสารและ chunks
        document_id = "doc123"
        document = await document_service.get_document(document_id)
        assert document is not None, "ไม่พบเอกสารที่ต้องการ"
        
        chunks = await document_service.get_document_chunks(document_id)
        assert len(chunks) > 0, "ไม่พบ chunks ในเอกสาร"
        
        # สร้าง embeddings สำหรับทุก chunk
        embeddings = await embedding_service.create_embeddings_for_document(document_id, chunks)
        assert len(embeddings) == len(chunks), "จำนวน embeddings ไม่ตรงกับจำนวน chunks"
        
        # ตรวจสอบว่า embeddings ที่ได้มีโครงสร้างที่ถูกต้อง
        for embedding in embeddings:
            assert "id" in embedding, "embedding ไม่มี id"
            assert "embedding" in embedding, "embedding ไม่มี vector"
            assert len(embedding["embedding"]) == 384, "ขนาดของ embedding ไม่ถูกต้อง"
    
    @pytest.mark.asyncio
    async def test_embedding_creation_for_query(self, embedding_service):
        """ทดสอบการสร้าง Embedding สำหรับคำค้นหา"""
        # สร้าง embedding สำหรับคำค้นหา
        query = "การวางแผนยุทธศาสตร์"
        embedding = await embedding_service.create_embedding(query)
        
        # ตรวจสอบผลลัพธ์
        assert embedding is not None, "ไม่สามารถสร้าง embedding สำหรับคำค้นหาได้"
        assert len(embedding) == 384, "ขนาดของ embedding ไม่ถูกต้อง"
    
    @pytest.mark.asyncio
    async def test_get_embedding_by_chunk_id(self, embedding_service):
        """ทดสอบการดึง Embedding โดยใช้ chunk ID"""
        # ดึง embedding โดยใช้ chunk ID
        chunk_id = "chunk1"
        embedding = await embedding_service.get_embedding(chunk_id)
        
        # ตรวจสอบผลลัพธ์
        assert embedding is not None, "ไม่สามารถดึง embedding จาก chunk ID ได้"
        assert len(embedding) == 384, "ขนาดของ embedding ไม่ถูกต้อง"
    
    @pytest.mark.asyncio
    async def test_embedding_pipeline_with_error_handling(self, embedding_service, document_service):
        """ทดสอบกระบวนการ embedding พร้อมการจัดการข้อผิดพลาด"""
        # ทดสอบกับเอกสารที่ไม่มีอยู่จริง
        document_id = "non_existent_doc"
        document = await document_service.get_document(document_id)
        assert document is None, "ไม่ควรพบเอกสารที่ไม่มีอยู่จริง"
        
        # ดึง chunks และตรวจสอบว่าเป็นลิสต์ว่าง
        chunks = await document_service.get_document_chunks(document_id)
        assert len(chunks) == 0, "ไม่ควรพบ chunks ในเอกสารที่ไม่มีอยู่จริง"
        
        # ทดสอบการสร้าง embeddings สำหรับลิสต์ว่าง
        embeddings = await embedding_service.create_embeddings_for_document(document_id, chunks)
        assert len(embeddings) == 0, "ควรได้ลิสต์ว่างเมื่อสร้าง embeddings สำหรับลิสต์ chunks ว่าง"

# การรันการทดสอบแบบ standalone (ไม่ผ่าน pytest)
if __name__ == "__main__":
    # สร้าง mock event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # สร้าง services
    embedding_service = MockEmbeddingService()
    document_service = MockDocumentService()
    
    # ทดสอบ create_embedding
    embedding = loop.run_until_complete(embedding_service.create_embedding("ทดสอบ"))
    print(f"Embedding size: {len(embedding)}")
    
    # ทดสอบ get_document_chunks
    chunks = loop.run_until_complete(document_service.get_document_chunks("doc123"))
    print(f"Number of chunks: {len(chunks)}")
    
    # ทดสอบ create_embeddings_for_document
    embeddings = loop.run_until_complete(embedding_service.create_embeddings_for_document("doc123", chunks))
    print(f"Number of embeddings: {len(embeddings)}")
    
    # ปิด event loop
    loop.close()