import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import app และ services ที่จะทดสอบ (ให้แก้ import path ตามโครงสร้างโปรเจคจริง)
# from app.main import app
# from app.services.document_service import document_service
# from app.services.search_service import search_service
# from app.services.claude_service import claude_service

# สร้าง mock app สำหรับการทดสอบ
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body
from typing import Dict, List, Optional, Any

# สร้าง mock app สำหรับการทดสอบ
mock_app = FastAPI()

@mock_app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "neo4j": "healthy",
            "chroma": "healthy"
        },
        "timestamp": "current_timestamp"
    }

@mock_app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    subcategory: str = Form(...)
):
    return {
        "id": "doc123",
        "filename": file.filename,
        "category": category,
        "subcategory": subcategory,
        "status": "processing"
    }

@mock_app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str):
    if document_id == "doc123":
        return {
            "id": "doc123",
            "filename": "test.pdf",
            "category": "หมวด_1",
            "subcategory": "1.1",
            "content": "Test content",
            "status": "processed"
        }
    raise HTTPException(status_code=404, detail="Document not found")

@mock_app.post("/api/v1/search/hybrid")
async def hybrid_search(query: Dict[str, Any] = Body(...)):
    return {
        "results": [
            {
                "id": "chunk1",
                "document_id": "doc123",
                "content": "Test content about strategic planning",
                "category": "หมวด_2",
                "score": 0.85
            },
            {
                "id": "chunk2",
                "document_id": "doc456",
                "content": "Another test content about PMQA criteria",
                "category": "หมวด_1",
                "score": 0.75
            }
        ]
    }

@mock_app.post("/api/v1/claude/ask")
async def ask_claude(question: Dict[str, str] = Body(...)):
    return {
        "answer": "นี่คือคำตอบจาก Claude AI เกี่ยวกับเกณฑ์ PMQA 4.0",
        "sources": [
            {
                "document_id": "doc123",
                "chunk_id": "chunk1",
                "content": "Test content about strategic planning"
            }
        ]
    }

@mock_app.get("/api/v1/pmqa/structure")
async def get_pmqa_structure():
    return {
        "categories": [
            {
                "id": "หมวด_1",
                "name": "การนำองค์การ",
                "subcategories": [
                    {"id": "1.1", "name": "การนำองค์การโดยผู้บริหารของส่วนราชการ"},
                    {"id": "1.2", "name": "การกำกับดูแลองค์การและการสร้างคุณูปการต่อสังคม"}
                ]
            },
            {
                "id": "หมวด_2",
                "name": "การวางแผนเชิงยุทธศาสตร์",
                "subcategories": [
                    {"id": "2.1", "name": "แผนปฏิบัติการประจำปีที่ตอบสนองความท้าทาย"},
                    {"id": "2.2", "name": "เป้าหมายสอดรับยุทธศาสตร์ชาติทั้งระยะสั้นและระยะยาว"}
                ]
            }
        ]
    }

# การทดสอบ API Endpoints
@pytest.mark.api
class TestAPIEndpoints:
    
    @pytest.fixture
    def client(self):
        """สร้าง TestClient สำหรับการทดสอบ API"""
        # สำหรับการทดสอบจริง ให้ใช้ app จริงๆ
        # return TestClient(app)
        
        # สำหรับตัวอย่างนี้ ใช้ mock app แทน
        return TestClient(mock_app)
    
    def test_health_check_endpoint(self, client):
        """ทดสอบ health check endpoint"""
        response = client.get("/api/v1/health")
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["api"] == "healthy"
        assert data["services"]["neo4j"] == "healthy"
        assert data["services"]["chroma"] == "healthy"
    
    def test_upload_document_endpoint(self, client):
        """ทดสอบ upload document endpoint"""
        # สร้างไฟล์ทดสอบ
        files = {"file": ("test.pdf", b"test content", "application/pdf")}
        data = {"category": "หมวด_1", "subcategory": "1.1"}
        
        # ส่งคำขอ
        response = client.post(
            "/api/v1/documents/upload",
            files=files,
            data=data
        )
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert data["id"] == "doc123"
        assert data["filename"] == "test.pdf"
        assert data["category"] == "หมวด_1"
        assert data["subcategory"] == "1.1"
        assert data["status"] == "processing"
    
    def test_get_document_endpoint(self, client):
        """ทดสอบ get document endpoint"""
        # ส่งคำขอสำหรับเอกสารที่มีอยู่
        response = client.get("/api/v1/documents/doc123")
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert data["id"] == "doc123"
        assert data["filename"] == "test.pdf"
        assert data["category"] == "หมวด_1"
        assert data["status"] == "processed"
        
        # ส่งคำขอสำหรับเอกสารที่ไม่มีอยู่
        response = client.get("/api/v1/documents/non_existent_doc")
        
        # ตรวจสอบ status code
        assert response.status_code == 404
    
    def test_hybrid_search_endpoint(self, client):
        """ทดสอบ hybrid search endpoint"""
        # ส่งคำขอค้นหา
        response = client.post(
            "/api/v1/search/hybrid",
            json={"query": "การวางแผนยุทธศาสตร์", "limit": 5}
        )
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        
        # ตรวจสอบโครงสร้างของผลลัพธ์
        result = data["results"][0]
        assert "id" in result
        assert "document_id" in result
        assert "content" in result
        assert "category" in result
        assert "score" in result
    
    def test_ask_claude_endpoint(self, client):
        """ทดสอบ ask Claude endpoint"""
        # ส่งคำขอถาม Claude
        response = client.post(
            "/api/v1/claude/ask",
            json={"question": "อธิบายเกณฑ์ PMQA 4.0 หมวดที่ 1"}
        )
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
        
        # ตรวจสอบโครงสร้างของแหล่งอ้างอิง
        source = data["sources"][0]
        assert "document_id" in source
        assert "chunk_id" in source
        assert "content" in source
    
    def test_get_pmqa_structure_endpoint(self, client):
        """ทดสอบ get PMQA structure endpoint"""
        # ส่งคำขอดึงโครงสร้าง PMQA
        response = client.get("/api/v1/pmqa/structure")
        
        # ตรวจสอบ status code
        assert response.status_code == 200
        
        # ตรวจสอบเนื้อหาการตอบกลับ
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # ตรวจสอบโครงสร้างของหมวดหมู่
        category = data["categories"][0]
        assert "id" in category
        assert "name" in category
        assert "subcategories" in category
        assert len(category["subcategories"]) > 0
        
        # ตรวจสอบโครงสร้างของหมวดหมู่ย่อย
        subcategory = category["subcategories"][0]
        assert "id" in subcategory
        assert "name" in subcategory