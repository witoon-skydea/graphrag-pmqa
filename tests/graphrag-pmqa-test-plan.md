# GraphRAG for PMQA 4.0 - ชุดทดสอบแบบละเอียด

## 1. บทนำ

เอกสารนี้ประกอบด้วยชุดทดสอบอย่างละเอียดสำหรับระบบ GraphRAG for PMQA 4.0 โดยรวมถึงการทดสอบหน่วย (Unit Testing), การทดสอบการทำงานร่วมกัน (Integration Testing), การทดสอบระบบ (System Testing), การทดสอบการใช้งาน (Usability Testing), และการทดสอบประสิทธิภาพ (Performance Testing)

### 1.1 วัตถุประสงค์

- ตรวจสอบว่าแต่ละองค์ประกอบของระบบทำงานตามที่ออกแบบไว้
- ตรวจสอบว่าองค์ประกอบทั้งหมดทำงานร่วมกันได้อย่างถูกต้อง
- ตรวจสอบว่าระบบทั้งหมดมีความเสถียรและมีประสิทธิภาพสูง
- ระบุและแก้ไขข้อบกพร่องและปัญหาก่อนการปล่อยใช้งานจริง

### 1.2 สภาพแวดล้อมการทดสอบ

- **สภาพแวดล้อมการพัฒนา**: Docker Compose ที่ประกอบด้วย Neo4j, Ollama, Backend (FastAPI), และ Frontend (Streamlit)
- **สภาพแวดล้อมการทดสอบ**: เหมือนกับสภาพแวดล้อมการพัฒนา
- **เครื่องมือที่ใช้ในการทดสอบ**: pytest, pytest-cov, pytest-asyncio, httpx, pytest-mock

## 2. แผนการทดสอบหน่วย (Unit Testing)

### 2.1 โครงสร้างการทดสอบหน่วย

```
/hope_x1/tests/
├── unit/
│   ├── test_config.py
│   ├── test_logging.py
│   ├── test_db/
│   │   ├── test_graph_db.py
│   │   └── test_vector_db.py
│   ├── test_models/
│   │   ├── test_document.py
│   │   ├── test_pmqa.py
│   │   └── test_search.py
│   ├── test_services/
│   │   ├── test_document_service.py
│   │   ├── test_embedding_service.py
│   │   ├── test_entity_service.py
│   │   ├── test_graphrag_service.py
│   │   └── test_claude_service.py
│   └── test_utils/
│       ├── test_text_splitter.py
│       └── test_metadata_extractor.py
```

### 2.2 การทดสอบโมดูลหลัก

#### 2.2.1 การทดสอบการกำหนดค่า (Configuration)

```python
# /hope_x1/tests/unit/test_config.py

import os
import pytest
from app.core.config import Settings, get_settings

def test_default_settings():
    """ตรวจสอบว่าค่าเริ่มต้นถูกกำหนดอย่างถูกต้อง"""
    settings = Settings()
    assert settings.PROJECT_NAME == "GraphRAG PMQA"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.EMBEDDING_MODEL == "nomic-embed-text"
    # ทดสอบค่าเริ่มต้นอื่นๆ

def test_env_settings(monkeypatch):
    """ตรวจสอบว่าการตั้งค่าจากตัวแปรสภาพแวดล้อมทำงานอย่างถูกต้อง"""
    monkeypatch.setenv("PROJECT_NAME", "Test Project")
    monkeypatch.setenv("NEO4J_URI", "bolt://neo4j-test:7687")
    
    settings = get_settings()
    assert settings.PROJECT_NAME == "Test Project"
    assert settings.NEO4J_URI == "bolt://neo4j-test:7687"
```

#### 2.2.2 การทดสอบการบันทึกข้อมูล (Logging)

```python
# /hope_x1/tests/unit/test_logging.py

import logging
import pytest
from app.core.logging import setup_logging

def test_setup_logging(caplog):
    """ตรวจสอบว่าการตั้งค่าการบันทึกข้อมูลทำงานอย่างถูกต้อง"""
    setup_logging()
    
    logger = logging.getLogger("app")
    logger.info("Test log message")
    
    assert "Test log message" in caplog.text
    assert "INFO" in caplog.text
```

#### 2.2.3 การทดสอบการเชื่อมต่อฐานข้อมูล

```python
# /hope_x1/tests/unit/test_db/test_graph_db.py

import pytest
from unittest.mock import patch, MagicMock
from app.db.graph_db import GraphDatabase, graph_db

@pytest.fixture
def mock_neo4j():
    with patch("app.db.graph_db.Neo4jDriver") as mock:
        yield mock

def test_graph_db_initialization(mock_neo4j):
    """ตรวจสอบว่าการเริ่มต้นฐานข้อมูลกราฟทำงานอย่างถูกต้อง"""
    db = GraphDatabase("bolt://localhost:7687", "neo4j", "password")
    mock_neo4j.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))

def test_get_session(mock_neo4j):
    """ตรวจสอบว่าการสร้าง session ทำงานอย่างถูกต้อง"""
    mock_session = MagicMock()
    mock_neo4j.return_value.session.return_value = mock_session
    
    db = GraphDatabase("bolt://localhost:7687", "neo4j", "password")
    session = db.get_session()
    
    assert session == mock_session
    mock_neo4j.return_value.session.assert_called_once()
```

### 2.3 การทดสอบ API Endpoints

#### 2.3.1 การทดสอบ Document API

```python
# /hope_x1/tests/unit/test_api/test_documents_api.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_document_service():
    with patch("app.api.documents.document_service") as mock:
        yield mock

def test_upload_document(mock_document_service):
    """ทดสอบการอัปโหลดเอกสาร"""
    mock_document_service.upload_document.return_value = {
        "id": "doc123",
        "filename": "test.pdf",
        "category": "หมวด_1",
        "subcategory": "1.1",
        "status": "processed"
    }
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", b"test content", "application/pdf")},
        data={"category": "หมวด_1", "subcategory": "1.1"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "doc123"
    assert response.json()["filename"] == "test.pdf"
    mock_document_service.upload_document.assert_called_once()

def test_get_document(mock_document_service):
    """ทดสอบการดึงข้อมูลเอกสาร"""
    mock_document_service.get_document.return_value = {
        "id": "doc123",
        "filename": "test.pdf",
        "category": "หมวด_1",
        "subcategory": "1.1",
        "content": "Test content",
        "status": "processed"
    }
    
    response = client.get("/api/v1/documents/doc123")
    
    assert response.status_code == 200
    assert response.json()["id"] == "doc123"
    mock_document_service.get_document.assert_called_once_with("doc123")
```

## 3. แผนการทดสอบการทำงานร่วมกัน (Integration Testing)

### 3.1 โครงสร้างการทดสอบการทำงานร่วมกัน

```
/hope_x1/tests/
├── integration/
│   ├── test_db_integration.py
│   ├── test_embedding_pipeline.py
│   ├── test_graph_vector_search.py
│   ├── test_document_processing.py
│   └── test_claude_integration.py
```

### 3.2 การทดสอบการทำงานร่วมกันของโมดูลต่างๆ

#### 3.2.1 การทดสอบการประมวลผลเอกสาร

```python
# /hope_x1/tests/integration/test_document_processing.py

import pytest
import os
import tempfile
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.entity_service import EntityService

@pytest.fixture
def sample_pdf():
    """สร้างไฟล์ PDF ตัวอย่างสำหรับการทดสอบ"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        # สร้างไฟล์ PDF อย่างง่าย (ในการทดสอบจริงอาจใช้ PyPDF2 หรือ ReportLab)
        f.write(b"%PDF-1.4\nTest PMQA document content")
        temp_path = f.name
    
    yield temp_path
    os.unlink(temp_path)

@pytest.mark.asyncio
async def test_document_processing_pipeline(sample_pdf):
    """ทดสอบกระบวนการประมวลผลเอกสารทั้งหมด"""
    # ตั้งค่าบริการที่เกี่ยวข้อง
    doc_service = DocumentService()
    embed_service = EmbeddingService()
    entity_service = EntityService()
    
    # อัปโหลดและประมวลผลเอกสาร
    with open(sample_pdf, "rb") as f:
        document_id = await doc_service.upload_document(
            file=f,
            filename="test.pdf",
            category="หมวด_1",
            subcategory="1.1"
        )
    
    # ตรวจสอบว่าเอกสารถูกบันทึกลงในฐานข้อมูล
    document = await doc_service.get_document(document_id)
    assert document is not None
    assert document["filename"] == "test.pdf"
    assert document["category"] == "หมวด_1"
    
    # ตรวจสอบว่า embeddings ถูกสร้างขึ้น
    chunks = await doc_service.get_document_chunks(document_id)
    assert len(chunks) > 0
    
    for chunk in chunks:
        embedding = await embed_service.get_embedding(chunk["id"])
        assert embedding is not None
        assert len(embedding) > 0
    
    # ตรวจสอบว่าเอนทิตีถูกแยกแยะและบันทึก
    entities = await entity_service.get_document_entities(document_id)
    assert len(entities) > 0
```

#### 3.2.2 การทดสอบการค้นหาแบบผสม (Hybrid Search)

```python
# /hope_x1/tests/integration/test_graph_vector_search.py

import pytest
from app.services.graphrag_service import GraphRAGService
from app.services.embedding_service import EmbeddingService

@pytest.mark.asyncio
async def test_hybrid_search():
    """ทดสอบการค้นหาแบบผสมระหว่าง Graph และ Vector"""
    # ตั้งค่าบริการที่เกี่ยวข้อง
    graphrag_service = GraphRAGService()
    embed_service = EmbeddingService()
    
    # สร้าง embedding สำหรับคำค้นหา
    query = "การวางแผนยุทธศาสตร์ของหน่วยงานภาครัฐ"
    query_embedding = await embed_service.create_embedding(query)
    
    # ทำการค้นหาแบบผสม
    results = await graphrag_service.hybrid_search(
        query=query,
        query_embedding=query_embedding,
        category="หมวด_2",  # กำหนดหมวดเป็นตัวกรอง
        limit=5
    )
    
    # ตรวจสอบผลลัพธ์
    assert len(results) > 0
    for result in results:
        assert "content" in result
        assert "document_id" in result
        assert "category" in result
        assert "score" in result
        assert result["score"] > 0.0
```

## 4. แผนการทดสอบระบบ (System Testing)

### 4.1 การทดสอบระบบ End-to-End

#### 4.1.1 การทดสอบการอัปโหลดและค้นหาเอกสาร

```python
# /hope_x1/tests/system/test_document_upload_search.py

import pytest
import os
import time
import requests
from pathlib import Path

BACKEND_URL = "http://localhost:8000/api/v1"
SAMPLE_FILES_DIR = Path(__file__).parent / "sample_files"

def test_upload_search_document():
    """ทดสอบการอัปโหลดเอกสารและค้นหาข้อมูลในเอกสารนั้น"""
    # ตรวจสอบว่า API ทำงานอยู่
    health_check = requests.get(f"{BACKEND_URL}/health")
    assert health_check.status_code == 200
    assert health_check.json()["status"] == "healthy"
    
    # อัปโหลดเอกสารตัวอย่าง
    sample_pdf = SAMPLE_FILES_DIR / "sample_pmqa_document.pdf"
    with open(sample_pdf, "rb") as f:
        files = {"file": (sample_pdf.name, f, "application/pdf")}
        data = {"category": "หมวด_2", "subcategory": "2.1"}
        
        upload_resp = requests.post(
            f"{BACKEND_URL}/documents/upload",
            files=files,
            data=data
        )
    
    assert upload_resp.status_code == 200
    document_id = upload_resp.json()["id"]
    
    # รอให้เอกสารถูกประมวลผลเสร็จสิ้น
    max_retries = 10
    retries = 0
    processed = False
    
    while retries < max_retries and not processed:
        time.sleep(2)  # รอ 2 วินาที
        doc_status = requests.get(f"{BACKEND_URL}/documents/{document_id}")
        if doc_status.json()["status"] == "processed":
            processed = True
        retries += 1
    
    assert processed, "เอกสารไม่ถูกประมวลผลภายในเวลาที่กำหนด"
    
    # ค้นหาข้อมูลในเอกสาร
    search_query = "ยุทธศาสตร์ องค์กร"
    search_resp = requests.post(
        f"{BACKEND_URL}/search/hybrid",
        json={"query": search_query, "limit": 5}
    )
    
    assert search_resp.status_code == 200
    results = search_resp.json()["results"]
    assert len(results) > 0
    
    # ตรวจสอบว่าเอกสารที่เพิ่งอัปโหลดอยู่ในผลการค้นหา
    found = any(result["document_id"] == document_id for result in results)
    assert found, "เอกสารที่อัปโหลดไม่ถูกพบในผลการค้นหา"
```

#### 4.1.2 การทดสอบการถามตอบกับ Claude AI

```python
# /hope_x1/tests/system/test_claude_qa.py

import pytest
import requests
import time

BACKEND_URL = "http://localhost:8000/api/v1"

def test_claude_qa():
    """ทดสอบการถาม-ตอบกับ Claude AI"""
    # ตรวจสอบว่า API ทำงานอยู่
    health_check = requests.get(f"{BACKEND_URL}/health")
    assert health_check.status_code == 200
    
    # ส่งคำถามไปยัง Claude AI
    question = "อธิบายเกณฑ์ PMQA 4.0 หมวดที่ 2 เกี่ยวกับการวางแผนเชิงยุทธศาสตร์"
    
    qa_resp = requests.post(
        f"{BACKEND_URL}/claude/ask",
        json={"question": question}
    )
    
    assert qa_resp.status_code == 200
    result = qa_resp.json()
    
    # ตรวจสอบผลลัพธ์
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert "sources" in result
    assert len(result["sources"]) > 0
    
    # ตรวจสอบว่าคำตอบมีความเกี่ยวข้องกับคำถาม
    answer = result["answer"].lower()
    assert "หมวด" in answer or "pmqa" in answer or "วางแผน" in answer or "ยุทธศาสตร์" in answer
```

### 4.2 การทดสอบความมั่นคงของระบบ

#### 4.2.1 การทดสอบการกู้คืนระบบ

```python
# /hope_x1/tests/system/test_system_resilience.py

import pytest
import requests
import subprocess
import time

BACKEND_URL = "http://localhost:8000/api/v1"

def test_system_recovery():
    """ทดสอบการกู้คืนระบบหลังจากการรีสตาร์ท"""
    # ตรวจสอบสถานะระบบก่อนการรีสตาร์ท
    health_check = requests.get(f"{BACKEND_URL}/health")
    assert health_check.status_code == 200
    assert health_check.json()["status"] == "healthy"
    
    # รีสตาร์ทบริการ backend
    subprocess.run(["docker-compose", "restart", "backend"], check=True)
    
    # รอให้บริการกลับมาออนไลน์
    max_retries = 10
    retries = 0
    recovered = False
    
    while retries < max_retries and not recovered:
        time.sleep(3)  # รอ 3 วินาที
        try:
            health_check = requests.get(f"{BACKEND_URL}/health")
            if health_check.status_code == 200 and health_check.json()["status"] == "healthy":
                recovered = True
        except requests.exceptions.ConnectionError:
            pass
        retries += 1
    
    assert recovered, "ระบบไม่สามารถกลับมาใช้งานได้หลังจากการรีสตาร์ท"
    
    # ทดสอบว่าฟังก์ชันหลักยังทำงานได้
    search_query = "ยุทธศาสตร์"
    search_resp = requests.post(
        f"{BACKEND_URL}/search/hybrid",
        json={"query": search_query, "limit": 5}
    )
    
    assert search_resp.status_code == 200
    assert len(search_resp.json()["results"]) >= 0
```

## 5. แผนการทดสอบการใช้งาน (Usability Testing)

### 5.1 การทดสอบ User Interface

#### 5.1.1 สคริปต์การทดสอบหน้า UI หลัก

```
# /hope_x1/tests/usability/frontend_test_script.md

# สคริปต์การทดสอบหน้า UI หลัก

## 1. การทดสอบหน้าอัปโหลดเอกสาร

### ขั้นตอนการทดสอบ
1. เข้าสู่ระบบที่ URL: http://localhost:8501
2. นำทางไปยังหน้า "อัปโหลดเอกสาร"
3. คลิกที่ปุ่ม "Browse files" และเลือกไฟล์ PDF ตัวอย่าง
4. เลือกหมวดหมู่ "หมวด_1" และหมวดหมู่ย่อย "1.1"
5. คลิกที่ปุ่ม "อัปโหลด"
6. รอให้การประมวลผลเสร็จสิ้น

### ผลลัพธ์ที่คาดหวัง
- ปุ่ม "Browse files" ควรเปิดหน้าต่างเลือกไฟล์ได้
- ควรมีรายการเลือกสำหรับหมวดหมู่และหมวดหมู่ย่อย
- ควรแสดงตัวบ่งชี้การโหลดในระหว่างการอัปโหลด
- เมื่อการประมวลผลเสร็จสิ้น ควรแสดงข้อความยืนยันพร้อมลิงก์ไปยังเอกสารที่อัปโหลด

## 2. การทดสอบหน้าค้นหาข้อมูล

### ขั้นตอนการทดสอบ
1. นำทางไปยังหน้า "ค้นหาข้อมูล"
2. ป้อนคำค้นหา "การวางแผนยุทธศาสตร์"
3. เลือกประเภทการค้นหาเป็น "Hybrid"
4. คลิกที่ปุ่ม "ค้นหา"
5. ตรวจสอบผลลัพธ์
6. ทดลองใช้ตัวกรองต่างๆ เช่น เลือกหมวดหมู่ "หมวด_2"
7. ทดลองคลิกที่ผลลัพธ์เพื่อดูรายละเอียด

### ผลลัพธ์ที่คาดหวัง
- ช่องค้นหาควรรับข้อความได้อย่างถูกต้อง
- ควรมีตัวเลือกสำหรับประเภทการค้นหา (Vector, Graph, Hybrid)
- ควรแสดงตัวบ่งชี้การโหลดในระหว่างการค้นหา
- ผลลัพธ์ควรแสดงในรูปแบบที่อ่านง่ายพร้อมเนื้อหาที่เกี่ยวข้อง
- ตัวกรองควรทำงานได้อย่างถูกต้องและกรองผลลัพธ์ตามที่เลือก
- การคลิกที่ผลลัพธ์ควรแสดงรายละเอียดเพิ่มเติมได้

## 3. การทดสอบหน้าถาม-ตอบกับ Claude AI

### ขั้นตอนการทดสอบ
1. นำทางไปยังหน้า "ถาม-ตอบกับ Claude AI"
2. ป้อนคำถาม "อธิบายเกณฑ์ PMQA 4.0 หมวดที่ 1"
3. คลิกที่ปุ่ม "ถาม"
4. รอให้ระบบประมวลผลคำตอบ
5. ตรวจสอบคำตอบและแหล่งอ้างอิง
6. ทดลองถามคำถามต่อเนื่อง

### ผลลัพธ์ที่คาดหวัง
- ช่องคำถามควรรับข้อความได้อย่างถูกต้อง
- ควรแสดงตัวบ่งชี้การโหลดในระหว่างการประมวลผล
- คำตอบควรแสดงในรูปแบบที่อ่านง่ายและมีการจัดรูปแบบที่ดี
- ควรแสดงแหล่งอ้างอิงที่ชัดเจนพร้อมลิงก์ไปยังเอกสารต้นฉบับ
- การถามคำถามต่อเนื่องควรสามารถเข้าใจบริบทของการสนทนาได้
```

### 5.2 การทดสอบความเร็วและการตอบสนอง

```bash
# /hope_x1/tests/usability/load_time_test.sh

#!/bin/bash

# ทดสอบความเร็วในการโหลดหน้า UI และการตอบสนองของ API

echo "ทดสอบความเร็วในการโหลดหน้า UI และการตอบสนองของ API"
echo "--------------------------------------------------"

# ทดสอบความเร็วในการตอบสนองของ API
echo "ทดสอบความเร็วในการตอบสนองของ API:"
time curl -s -o /dev/null -w "%{time_total}s\n" http://localhost:8000/api/v1/health

# ทดสอบความเร็วในการค้นหา
echo -e "\nทดสอบความเร็วในการค้นหา (Vector):"
time curl -s -X POST -H "Content-Type: application/json" \
  -d '{"query": "ยุทธศาสตร์", "limit": 5}' \
  -o /dev/null -w "%{time_total}s\n" \
  http://localhost:8000/api/v1/search/vector

echo -e "\nทดสอบความเร็วในการค้นหา (Graph):"
time curl -s -X POST -H "Content-Type: application/json" \
  -d '{"query": "ยุทธศาสตร์", "limit": 5}' \
  -o /dev/null -w "%{time_total}s\n" \
  http://localhost:8000/api/v1/search/graph

echo -e "\nทดสอบความเร็วในการค้นหา (Hybrid):"
time curl -s -X POST -H "Content-Type: application/json" \
  -d '{"query": "ยุทธศาสตร์", "limit": 5}' \
  -o /dev/null -w "%{time_total}s\n" \
  http://localhost:8000/api/v1/search/hybrid

# ทดสอบความเร็วในการถาม-ตอบกับ Claude AI
echo -e "\nทดสอบความเร็วในการถาม-ตอบกับ Claude AI:"
time curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question": "อธิบายเกณฑ์ PMQA 4.0 หมวดที่ 1"}' \
  -o /dev/null -w "%{time_total}s\n" \
  http://localhost:8000/api/v1/claude/ask

echo -e "\nการทดสอบเสร็จสิ้น"
```

## 6. แผนการทดสอบประสิทธิภาพ (Performance Testing)

### 6.1 การทดสอบโหลด (Load Testing)

```python
# /hope_x1/tests/performance/test_load.py

import pytest
import time
import asyncio
import aiohttp
import statistics
from concurrent.futures import ThreadPoolExecutor

BACKEND_URL = "http://localhost:8000/api/v1"
NUM_REQUESTS = 50
CONCURRENT_USERS = 10

async def fetch(session, url, json_data=None):
    start_time = time.time()
    
    if json_data:
        async with session.post(url, json=json_data) as response:
            await response.json()
    else:
        async with session.get(url) as response:
            await response.json()
            
    end_time = time.time()
    return end_time - start_time

async def run_load_test(endpoint, json_data=None, description=""):
    print(f"\nการทดสอบโหลด: {description}")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(NUM_REQUESTS):
            if json_data:
                task = fetch(session, f"{BACKEND_URL}/{endpoint}", json_data)
            else:
                task = fetch(session, f"{BACKEND_URL}/{endpoint}")
            tasks.append(task)
            
        response_times = await asyncio.gather(*tasks)
        
    # วิเคราะห์ผลลัพธ์
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    p95_time = sorted(response_times)[int(0.95 * len(response_times))]
    
    print(f"เวลาเฉลี่ย: {avg_time:.4f}s")
    print(f"เวลาต่ำสุด: {min_time:.4f}s")
    print(f"เวลาสูงสุด: {max_time:.4f}s")
    print(f"เวลา P95: {p95_time:.4f}s")
    print(f"จำนวนคำขอต่อวินาที: {NUM_REQUESTS / sum(response_times):.2f}")
    
    return {
        "avg": avg_time,
        "min": min_time,
        "max": max_time,
        "p95": p95_time,
        "rps": NUM_REQUESTS / sum(response_times)
    }

@pytest.mark.asyncio
async def test_health_endpoint_load():
    """ทดสอบโหลดที่ health endpoint"""
    results = await run_load_test("health", description="Health Endpoint")
    assert results["avg"] < 0.5  # เวลาเฉลี่ยควรน้อยกว่า 0.5 วินาที

@pytest.mark.asyncio
async def test_vector_search_load():
    """ทดสอบโหลดที่ vector search endpoint"""
    results = await run_load_test(
        "search/vector",
        json_data={"query": "ยุทธศาสตร์", "limit": 5},
        description="Vector Search"
    )
    assert results["avg"] < 2.0  # เวลาเฉลี่ยควรน้อยกว่า 2 วินาที

@pytest.mark.asyncio
async def test_hybrid_search_load():
    """ทดสอบโหลดที่ hybrid search endpoint"""
    results = await run_load_test(
        "search/hybrid",
        json_data={"query": "ยุทธศาสตร์", "limit": 5},
        description="Hybrid Search"
    )
    assert results["avg"] < 3.0  # เวลาเฉลี่ยควรน้อยกว่า 3 วินาที
```

### 6.2 การทดสอบความจุและการทนทาน (Capacity and Endurance Testing)

```python
# /hope_x1/tests/performance/test_capacity.py

import pytest
import asyncio
import aiohttp
import time
import json
import random
from pathlib import Path

BACKEND_URL = "http://localhost:8000/api/v1"
SAMPLE_FILES_DIR = Path(__file__).parent / "sample_files"
NUM_DOCUMENTS = 10  # จำนวนเอกสารที่จะอัปโหลด
TEST_DURATION = 60 * 5  # ทดสอบเป็นเวลา 5 นาที

async def upload_document(session, file_path, category, subcategory):
    """อัปโหลดเอกสารไปยัง API"""
    with open(file_path, "rb") as f:
        form_data = aiohttp.FormData()
        form_data.add_field("file", f, filename=file_path.name)
        form_data.add_field("category", category)
        form_data.add_field("subcategory", subcategory)
        
        async with session.post(f"{BACKEND_URL}/documents/upload", data=form_data) as response:
            result = await response.json()
            return result["id"] if response.status == 200 else None

async def run_search_query(session, query):
    """ดำเนินการค้นหาด้วยคำค้นหาที่กำหนด"""
    async with session.post(
        f"{BACKEND_URL}/search/hybrid",
        json={"query": query, "limit": 5}
    ) as response:
        return await response.json()

@pytest.mark.asyncio
async def test_system_capacity():
    """ทดสอบความจุของระบบโดยการอัปโหลดเอกสารจำนวนมาก"""
    # เตรียมเอกสารตัวอย่าง
    sample_files = list(SAMPLE_FILES_DIR.glob("*.pdf"))
    assert len(sample_files) > 0, "ไม่พบไฟล์ตัวอย่างสำหรับการทดสอบ"
    
    # กำหนดหมวดหมู่
    categories = ["หมวด_1", "หมวด_2", "หมวด_3", "หมวด_4", "หมวด_5", "หมวด_6", "หมวด_7"]
    subcategories = {
        "หมวด_1": ["1.1", "1.2", "1.3", "1.4"],
        "หมวด_2": ["2.1", "2.2", "2.3", "2.4"],
        "หมวด_3": ["3.1", "3.2", "3.3", "3.4"],
        "หมวด_4": ["4.1", "4.2", "4.3", "4.4"],
        "หมวด_5": ["5.1", "5.2", "5.3", "5.4"],
        "หมวด_6": ["6.1", "6.2", "6.3", "6.4"],
        "หมวด_7": ["7.1", "7.2", "7.3", "7.4"]
    }
    
    # อัปโหลดเอกสาร
    document_ids = []
    async with aiohttp.ClientSession() as session:
        for i in range(NUM_DOCUMENTS):
            file_path = random.choice(sample_files)
            category = random.choice(categories)
            subcategory = random.choice(subcategories[category])
            
            doc_id = await upload_document(session, file_path, category, subcategory)
            if doc_id:
                document_ids.append(doc_id)
                print(f"อัปโหลดเอกสาร {i+1}/{NUM_DOCUMENTS} สำเร็จ, ID: {doc_id}")
            else:
                print(f"การอัปโหลดเอกสาร {i+1}/{NUM_DOCUMENTS} ล้มเหลว")
    
    # รอให้เอกสารถูกประมวลผลเสร็จสิ้น
    print("รอให้เอกสารถูกประมวลผลเสร็จสิ้น...")
    time.sleep(30)  # รอ 30 วินาที
    
    # ทดสอบการค้นหาต่อเนื่อง
    search_queries = [
        "การวางแผนยุทธศาสตร์",
        "การบริหารจัดการองค์กร",
        "การพัฒนาบุคลากร",
        "การใช้เทคโนโลยีในหน่วยงานภาครัฐ",
        "การประเมินผลการปฏิบัติงาน",
        "การบริการประชาชน",
        "การปรับปรุงกระบวนการทำงาน"
    ]
    
    # ทดสอบค้นหาต่อเนื่อง
    print(f"เริ่มทดสอบการค้นหาต่อเนื่องเป็นเวลา {TEST_DURATION} วินาที...")
    start_time = time.time()
    query_count = 0
    success_count = 0
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < TEST_DURATION:
            query = random.choice(search_queries)
            try:
                result = await run_search_query(session, query)
                query_count += 1
                if "results" in result and len(result["results"]) > 0:
                    success_count += 1
            except Exception as e:
                print(f"การค้นหาล้มเหลว: {str(e)}")
            
            await asyncio.sleep(0.5)  # พักระหว่างคำขอ
    
    # รายงานผลลัพธ์
    duration = time.time() - start_time
    print(f"\nผลการทดสอบความจุและการทนทาน:")
    print(f"- จำนวนเอกสารที่อัปโหลด: {len(document_ids)}")
    print(f"- ระยะเวลาทดสอบ: {duration:.2f} วินาที")
    print(f"- จำนวนคำค้นหาทั้งหมด: {query_count}")
    print(f"- จำนวนคำค้นหาที่สำเร็จ: {success_count}")
    print(f"- อัตราความสำเร็จ: {success_count / query_count * 100:.2f}%")
    print(f"- คำค้นหาต่อวินาที: {query_count / duration:.2f}")
    
    # ตรวจสอบว่าอัตราความสำเร็จควรสูง
    assert success_count / query_count > 0.95, "อัตราความสำเร็จต่ำกว่า 95%"
```

## 7. การวางแผนการทดสอบสำหรับทีม QA

### 7.1 ขั้นตอนการดำเนินการทดสอบ

1. **เตรียมสภาพแวดล้อมการทดสอบ**
   - ตั้งค่า Docker Compose ในสภาพแวดล้อมการทดสอบ
   - สร้างและเตรียมข้อมูลตัวอย่างสำหรับใช้ในการทดสอบ

2. **การทดสอบหน่วย (Unit Testing)**
   - ให้นักพัฒนาเขียนและรันการทดสอบหน่วยสำหรับโมดูลที่ตนเองรับผิดชอบ
   - รวบรวมและเรียกใช้การทดสอบหน่วยทั้งหมดเพื่อตรวจสอบความครอบคลุม

3. **การทดสอบการทำงานร่วมกัน (Integration Testing)**
   - ทดสอบการทำงานร่วมกันของโมดูลต่างๆ เช่น การประมวลผลเอกสาร, การค้นหา
   - ตรวจสอบการเชื่อมต่อระหว่างส่วนประกอบต่างๆ ของระบบ

4. **การทดสอบระบบ (System Testing)**
   - ดำเนินการทดสอบแบบ End-to-End เพื่อตรวจสอบการทำงานของระบบทั้งหมด
   - ทดสอบการกู้คืนระบบและความทนทานของระบบ

5. **การทดสอบการใช้งาน (Usability Testing)**
   - ทดสอบหน้า UI ตามสคริปต์การทดสอบที่กำหนดไว้
   - ประเมินความเร็วและการตอบสนองของระบบ

6. **การทดสอบประสิทธิภาพ (Performance Testing)**
   - ดำเนินการทดสอบโหลดเพื่อวัดประสิทธิภาพภายใต้โหลดที่กำหนด
   - ทดสอบความจุและการทนทานของระบบในระยะยาว

### 7.2 ตารางเวลาการทดสอบ

| วัน | กิจกรรม | ผู้รับผิดชอบ |
|-----|---------|-------------|
| วันที่ 1 | เตรียมสภาพแวดล้อมการทดสอบและเครื่องมือ | QA Engineer, DevOps Engineer |
| วันที่ 2 | ดำเนินการทดสอบหน่วย | QA Engineer, Developer |
| วันที่ 3 | ดำเนินการทดสอบการทำงานร่วมกัน | QA Engineer, Developer |
| วันที่ 4 | ดำเนินการทดสอบระบบ | QA Engineer |
| วันที่ 5 | ดำเนินการทดสอบการใช้งาน | QA Engineer, UI/UX Designer |
| วันที่ 6 | ดำเนินการทดสอบประสิทธิภาพ | QA Engineer, DevOps Engineer |
| วันที่ 7 | วิเคราะห์ผลการทดสอบและรายงาน | QA Engineer, ทีมพัฒนาทั้งหมด |

### 7.3 รายการตรวจสอบก่อนการปล่อยใช้งาน (Pre-Release Checklist)

- [ ] การทดสอบหน่วยทั้งหมดผ่าน
- [ ] การทดสอบการทำงานร่วมกันทั้งหมดผ่าน
- [ ] การทดสอบระบบทั้งหมดผ่าน
- [ ] การทดสอบการใช้งานทั้งหมดผ่าน
- [ ] การทดสอบประสิทธิภาพทั้งหมดผ่าน
- [ ] ไม่มีปัญหาความปลอดภัยที่รู้จัก
- [ ] ตรวจสอบและปรับปรุงเอกสารให้ทันสมัย
- [ ] ตรวจสอบว่าการติดตั้งสำหรับผู้ใช้ทำงานได้อย่างถูกต้อง
- [ ] การสำรองข้อมูลและแผนการกู้คืนระบบพร้อมใช้งาน

## 8. สรุป

แผนการทดสอบนี้ครอบคลุมทุกด้านของระบบ GraphRAG for PMQA 4.0 ตั้งแต่การทดสอบหน่วยของแต่ละโมดูลไปจนถึงการทดสอบระบบทั้งหมดและการทดสอบประสิทธิภาพ การดำเนินการตามแผนการทดสอบนี้จะช่วยให้มั่นใจว่าระบบมีคุณภาพสูง มีเสถียรภาพ และพร้อมสำหรับการใช้งานจริง