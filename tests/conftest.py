import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import tempfile
import shutil

# กำหนดค่าสภาพแวดล้อมการทดสอบ
os.environ["TESTING"] = "True"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["CLAUDE_API_KEY"] = "dummy-api-key-for-testing"

# Fixtures สำหรับการทดสอบ
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """สร้าง TestClient สำหรับ FastAPI"""
    # Import ที่นี่เพื่อไม่ให้มีการเรียกใช้ app ตอนเริ่มต้น
    from app.main import app
    
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_neo4j_driver():
    """Mock สำหรับ Neo4j Driver"""
    with patch("app.db.graph_db.Neo4jDriver") as mock:
        yield mock

@pytest.fixture
def mock_chroma_client():
    """Mock สำหรับ ChromaDB Client"""
    with patch("app.db.vector_db.chromadb.PersistentClient") as mock:
        yield mock

@pytest.fixture
def mock_ollama_client():
    """Mock สำหรับ Ollama Client"""
    with patch("app.services.embedding_service.httpx.Client") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_claude_client():
    """Mock สำหรับ Claude API Client"""
    with patch("app.services.claude_service.anthropic.Anthropic") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def temp_document_dir():
    """สร้างไดเรกทอรีชั่วคราวสำหรับทดสอบเอกสาร"""
    temp_dir = tempfile.mkdtemp()
    os.environ["DOCUMENTS_BASE_DIR"] = temp_dir
    
    # สร้างโครงสร้างโฟลเดอร์หมวดหมู่
    for category in ["หมวด_1", "หมวด_2", "หมวด_3", "หมวด_4", "หมวด_5", "หมวด_6", "หมวด_7", "raw"]:
        os.makedirs(os.path.join(temp_dir, category), exist_ok=True)
    
    yield temp_dir
    
    # ลบไดเรกทอรีชั่วคราวเมื่อเสร็จสิ้นการทดสอบ
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_vector_db_dir():
    """สร้างไดเรกทอรีชั่วคราวสำหรับทดสอบ Vector Database"""
    temp_dir = tempfile.mkdtemp()
    os.environ["CHROMA_PERSIST_DIRECTORY"] = temp_dir
    
    yield temp_dir
    
    # ลบไดเรกทอรีชั่วคราวเมื่อเสร็จสิ้นการทดสอบ
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_pdf_content():
    """คืนค่าเนื้อหาตัวอย่างของไฟล์ PDF"""
    return b"%PDF-1.4\nTest PMQA document content about strategic planning and organizational management"

@pytest.fixture
def sample_pmqa_structure():
    """คืนค่าโครงสร้าง PMQA ตัวอย่าง"""
    return {
        "categories": [
            {
                "id": "หมวด_1",
                "name": "การนำองค์การ",
                "subcategories": [
                    {"id": "1.1", "name": "การนำองค์การโดยผู้บริหารของส่วนราชการ"},
                    {"id": "1.2", "name": "การกำกับดูแลองค์การและการสร้างคุณูปการต่อสังคม"},
                    {"id": "1.3", "name": "การมุ่งเน้นผลสัมฤทธิ์ผ่านการมีส่วนร่วมจากเครือข่าย"},
                    {"id": "1.4", "name": "การคำนึงถึงผลกระทบต่อสังคมและการมุ่งเน้นให้เกิดผลลัพธ์"}
                ]
            },
            {
                "id": "หมวด_2",
                "name": "การวางแผนเชิงยุทธศาสตร์",
                "subcategories": [
                    {"id": "2.1", "name": "แผนปฏิบัติการประจำปีที่ตอบสนองความท้าทาย สร้างนวัตกรรม การเปลี่ยนแปลง และมุ่งเน้นประโยชน์สุขประชาชน"},
                    {"id": "2.2", "name": "เป้าหมายสอดรับยุทธศาสตร์ชาติทั้งระยะสั้นและระยะยาว"},
                    {"id": "2.3", "name": "แผนขับเคลื่อนในทุกระดับและทุกภาคส่วน"},
                    {"id": "2.4", "name": "การติดตามผลของการบรรลุเป้าหมายเชิงยุทธศาสตร์ การแก้ไขปัญหา และการรายงานผล"}
                ]
            }
            # ... categories 3-7 would be included in a real implementation
        ]
    }