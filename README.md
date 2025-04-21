# GraphRAG for PMQA 4.0

ระบบจัดการและค้นหาข้อมูลตามโครงสร้าง PMQA 4.0 (Public Sector Management Quality Award) โดยเน้นการใช้ Graph Database และ Vector Search เพื่อเพิ่มประสิทธิภาพในการค้นหาและเรียกใช้ข้อมูลที่เกี่ยวข้อง

## ภาพรวม

ระบบนี้ช่วยให้องค์กรสามารถ:
- รวบรวมและจัดหมวดหมู่เอกสารตามโครงสร้าง PMQA 4.0
- ค้นหาข้อมูลที่เกี่ยวข้องได้อย่างแม่นยำและมีประสิทธิภาพ
- วิเคราะห์ความสัมพันธ์ระหว่างเอกสารและเกณฑ์ต่างๆ
- ตอบคำถามเกี่ยวกับ PMQA 4.0 โดยใช้ Claude AI

## เทคโนโลยีหลัก

ระบบใช้เทคโนโลยีหลักดังนี้:

- **Graph Database**: Neo4j Community Edition
- **Vector Database**: Chroma DB
- **Embedding Models**: nomic-embed-text หรือ jeffh/intfloat-multilingual-e5-large-instruct
- **Entity Analysis Models**: llama3, mistral (ผ่าน Ollama)
- **Backend**: Python, FastAPI
- **Frontend**: Streamlit
- **Question Answering**: Claude AI API

## โครงสร้างโปรเจค

```
/hope_x1/
├── app/                    # Backend API application
│   ├── api/                # API endpoints
│   ├── core/               # Core configurations
│   ├── db/                 # Database connections
│   ├── models/             # Data models
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions
│   └── main.py             # Main application entry point
├── data/                   # Data storage
│   ├── documents/          # Document storage
│   │   ├── หมวด_1/         # PMQA category 1 documents
│   │   ├── ...
│   │   └── raw/            # Raw uploaded documents
│   ├── chroma_db/          # Vector database storage
│   └── pmqa_structure.json # PMQA structure definition
├── frontend/               # Streamlit frontend
│   ├── pages/              # UI pages
│   ├── components/         # UI components
│   └── app.py              # Frontend entry point
├── scripts/                # Setup and utility scripts
├── tests/                  # Unit and integration tests
├── .env.example            # Environment variables example
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## การติดตั้ง

### ความต้องการของระบบ
- Python 3.10+
- Docker และ Docker Compose (แนะนำ)
- Neo4j Database
- Ollama (สำหรับ Embedding และ Entity Analysis)
- Claude API Key (สำหรับการถาม-ตอบ)

### การติดตั้งด้วย Docker

1. โคลนโปรเจคนี้:
   ```bash
   git clone <repository-url>
   cd hope_x1
   ```

2. สร้างไฟล์ .env จาก .env.example:
   ```bash
   cp .env.example .env
   ```

3. แก้ไขไฟล์ .env ตามความเหมาะสม โดยเฉพาะ `CLAUDE_API_KEY`

4. รัน Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. เข้าถึง:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - Neo4j Browser: http://localhost:7474

### การติดตั้งแบบ Local

1. โคลนโปรเจคนี้:
   ```bash
   git clone <repository-url>
   cd hope_x1
   ```

2. รันสคริปต์การติดตั้ง:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. รัน Backend:
   ```bash
   cd app
   uvicorn main:app --reload
   ```

4. รัน Frontend (ในอีก terminal หนึ่ง):
   ```bash
   cd frontend
   streamlit run app.py
   ```

## วิธีการใช้งาน

### การอัปโหลดเอกสาร
1. ไปที่หน้า "อัปโหลดเอกสาร"
2. เลือกไฟล์และกรอกข้อมูลที่เกี่ยวข้อง
3. คลิก "อัปโหลด"
4. ระบบจะวิเคราะห์และจัดหมวดหมู่เอกสารโดยอัตโนมัติ

### การค้นหาข้อมูล
1. ไปที่หน้า "ค้นหาข้อมูล"
2. ป้อนคำค้นหาและเลือกประเภทการค้นหา (Vector, Graph, หรือ Hybrid)
3. ปรับแต่งตัวกรองและตัวเลือกขั้นสูงตามความต้องการ
4. คลิก "ค้นหา"

### การถาม-ตอบกับ Claude AI
1. ไปที่หน้า "ถาม-ตอบกับ Claude AI"
2. ป้อนคำถามเกี่ยวกับ PMQA 4.0
3. ระบบจะค้นหาข้อมูลที่เกี่ยวข้องและส่งไปให้ Claude AI เพื่อสร้างคำตอบ
4. คำตอบจะแสดงพร้อมแหล่งอ้างอิง

## การพัฒนาเพิ่มเติม

### การเพิ่มโมเดลใหม่
สามารถเปลี่ยนโมเดลได้ใน .env หรือในไฟล์ app/core/config.py:
```
EMBEDDING_MODEL=<model-name>
ENTITY_MODEL=<model-name>
```

### การปรับแต่งประสิทธิภาพ
- ปรับขนาด chunk และค่า overlap ใน .env
- ปรับจำนวน documents และ chunks ที่ดึงมาในแต่ละครั้ง
- ปรับจำนวน contexts ที่ส่งให้ Claude AI

## การแก้ไขปัญหา

### ปัญหาการเชื่อมต่อ Neo4j
- ตรวจสอบว่า Neo4j กำลังทำงานและเข้าถึงได้ที่ URI ที่กำหนด
- ตรวจสอบรหัสผ่านและชื่อผู้ใช้

### ปัญหาการเชื่อมต่อ Ollama
- ตรวจสอบว่า Ollama กำลังทำงานและเข้าถึงได้ที่ URL ที่กำหนด
- ตรวจสอบว่ามีโมเดลที่ต้องการติดตั้งแล้ว

### ปัญหาการเชื่อมต่อ Claude API
- ตรวจสอบว่า API Key ถูกต้องและยังไม่หมดอายุ
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
