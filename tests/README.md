# GraphRAG for PMQA 4.0 - ชุดทดสอบ

ยินดีต้อนรับสู่ชุดทดสอบสำหรับโปรเจค GraphRAG for PMQA 4.0! เอกสารนี้จะแนะนำวิธีการใช้และจัดการชุดทดสอบทั้งหมด

## ภาพรวม

ชุดทดสอบนี้ออกแบบมาเพื่อทดสอบระบบ GraphRAG for PMQA 4.0 อย่างละเอียดในทุกด้าน ประกอบด้วยการทดสอบประเภทต่างๆ ดังนี้:
- การทดสอบหน่วย (Unit Testing)
- การทดสอบการทำงานร่วมกัน (Integration Testing)
- การทดสอบระบบ (System Testing)
- การทดสอบการใช้งาน (Usability Testing)
- การทดสอบประสิทธิภาพ (Performance Testing)

## เนื้อหาในชุดทดสอบ

โครงสร้างไฟล์ในชุดทดสอบ:
- **graphrag-pmqa-test-plan.md**: แผนการทดสอบละเอียดของโปรเจค
- **run-tests.sh**: สคริปต์สำหรับรันการทดสอบอัตโนมัติ
- **pytest.ini**: ไฟล์การกำหนดค่า pytest
- **conftest.py**: ไฟล์ fixture สำหรับการทดสอบ
- **test_document_service.py**: ตัวอย่างการทดสอบหน่วยสำหรับ DocumentService

## การติดตั้ง

สิ่งที่จำเป็นสำหรับการรันชุดทดสอบ:
- Python 3.10+
- Docker และ Docker Compose
- pytest และโมดูลที่เกี่ยวข้อง

ติดตั้ง dependencies สำหรับการทดสอบ:
```bash
pip install pytest pytest-cov pytest-asyncio httpx pytest-mock
```

## การใช้งาน

### การรันการทดสอบด้วยสคริปต์ run-tests.sh

1. ให้สิทธิ์การรันสคริปต์:
   ```bash
   chmod +x run-tests.sh
   ```

2. รันสคริปต์:
   ```bash
   ./run-tests.sh
   ```

3. เลือกประเภทการทดสอบจากเมนู

### การรันการทดสอบด้วย pytest โดยตรง

1. คัดลอกไฟล์ทดสอบไปยังโครงสร้างการทดสอบของโปรเจค:
   ```bash
   cp -r * /Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1/tests/
   ```

2. รันการทดสอบหน่วย:
   ```bash
   cd /Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1
   python -m pytest tests/unit -v
   ```

3. รันการทดสอบการทำงานร่วมกัน:
   ```bash
   python -m pytest tests/integration -v
   ```

4. รันการทดสอบระบบ:
   ```bash
   python -m pytest tests/system -v
   ```

5. รันการทดสอบประสิทธิภาพ:
   ```bash
   python -m pytest tests/performance -v
   ```

## การปรับแต่งการทดสอบ

### การเพิ่มไฟล์ทดสอบใหม่

1. สร้างไฟล์ทดสอบในไดเรกทอรีที่เหมาะสม:
   - `/tests/unit/` สำหรับการทดสอบหน่วย
   - `/tests/integration/` สำหรับการทดสอบการทำงานร่วมกัน
   - `/tests/system/` สำหรับการทดสอบระบบ
   - `/tests/performance/` สำหรับการทดสอบประสิทธิภาพ
   - `/tests/usability/` สำหรับการทดสอบการใช้งาน

2. ชื่อไฟล์ควรขึ้นต้นด้วย `test_` เช่น `test_search_service.py`

3. ชื่อคลาสทดสอบควรขึ้นต้นด้วย `Test` เช่น `TestSearchService`

4. ชื่อฟังก์ชันทดสอบควรขึ้นต้นด้วย `test_` เช่น `test_hybrid_search`

### การใช้ markers

สามารถใช้ markers เพื่อแยกประเภทการทดสอบ:
```python
@pytest.mark.unit
def test_my_function():
    ...
```

รันเฉพาะการทดสอบที่มี marker บางอย่าง:
```bash
python -m pytest -m "unit"
```

รันทุกการทดสอบยกเว้นที่มี marker บางอย่าง:
```bash
python -m pytest -m "not slow"
```

## การแก้ไขปัญหา

### การทดสอบล้มเหลวเนื่องจากข้อผิดพลาดในการเชื่อมต่อ

1. ตรวจสอบว่าบริการต่างๆ กำลังทำงานอยู่:
   ```bash
   cd /Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1
   docker-compose ps
   ```

2. รีสตาร์ทบริการถ้าจำเป็น:
   ```bash
   docker-compose restart
   ```

### การทดสอบล้มเหลวเนื่องจากตัวแปรสภาพแวดล้อมไม่ถูกต้อง

1. ตรวจสอบไฟล์ `.env`:
   ```bash
   cat /Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1/.env
   ```

2. สร้างหรือแก้ไขไฟล์ `.env` ถ้าจำเป็น:
   ```bash
   cp .env.example .env
   ```

## ผู้เขียนและการสนับสนุน

ติดต่อทีม QA Engineer สำหรับคำถามหรือความช่วยเหลือเกี่ยวกับชุดทดสอบนี้