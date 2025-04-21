# การออกแบบระบบ GraphRAG สำหรับ PMQA 4.0

## ภาพรวมของโครงการ

โครงการนี้มีวัตถุประสงค์เพื่อพัฒนาระบบ GraphRAG ที่จะช่วยจัดการข้อมูลตามโครงสร้าง PMQA 4.0 (7 หมวด) ซึ่งจะช่วยให้ลูกค้าสามารถจัดการข้อมูลที่กระจัดกระจายและค้นหาข้อมูลแบบเชื่อมโยงได้อย่างมีประสิทธิภาพ โดยระบบจะเชื่อมต่อกับ Claude AI เพื่อดึงข้อมูลตามประเด็นย่อยต่างๆ

## สถาปัตยกรรมระบบ

ระบบจะประกอบด้วยองค์ประกอบหลักดังนี้:

1. **Graph Database**: Neo4j Community Edition สำหรับจัดเก็บโครงสร้างความสัมพันธ์ของข้อมูล
2. **Vector Store**: Chroma DB สำหรับจัดเก็บ embeddings และค้นหาด้วย semantic search
3. **Document Storage**: ใช้ filesystem โดยตรงในการจัดเก็บเอกสาร
4. **Embedding Model**: nomic-embed-text:latest หรือ jeffh/intfloat-multilingual-e5-large-instruct:f16
5. **Entity Analysis Model**: llama3:latest หรือ mistral:latest
6. **Backend Framework**: FastAPI (Python)
7. **Frontend**: Streamlit หรือ Gradio

## โครงสร้างกราฟ

โครงสร้างกราฟจะประกอบด้วย:
- Nodes: Category, Subcategory, Criteria, Document, Chunk
- Relationships: HAS_SUBCATEGORY, HAS_CRITERIA, BELONGS_TO, HAS_CHUNK, RELATES_TO

## การทำงานของระบบ

1. **การนำเข้าเอกสาร**:
   - รับเอกสารจากลูกค้า
   - ประมวลผลและแบ่งเป็น chunks
   - สร้าง embeddings ด้วย nomic-embed-text หรือโมเดลที่เหมาะสม
   - วิเคราะห์หมวดหมู่ PMQA ด้วย llama3 หรือโมเดลที่เหมาะสม
   - สร้างความสัมพันธ์ในกราฟและจัดเก็บ embeddings

2. **การค้นหาข้อมูล**:
   - รับคำถามจากผู้ใช้/Claude
   - วิเคราะห์คำถามว่าเกี่ยวข้องกับหมวด PMQA ใด
   - ค้นหาด้วย vector similarity
   - ค้นหาด้วย graph traversal
   - รวมและจัดลำดับผลลัพธ์
   - ส่งข้อมูลที่เกี่ยวข้องให้ Claude AI

## ทรัพยากรที่ใช้

ระบบจะรันบน MacBook Air M2 RAM 24GB ซึ่งมีประสิทธิภาพเพียงพอในการรันโมเดลหลายตัวพร้อมกัน โดยสามารถ:
- รันโมเดล embedding และ entity analysis พร้อมกันได้
- ใช้ Neural Engine ของ M2 เพื่อเร่งการประมวลผล
- จัดการฐานข้อมูล Neo4j และ Vector DB ได้อย่างมีประสิทธิภาพ
- ประมวลผลเอกสารแบบ concurrent เพื่อเพิ่มประสิทธิภาพ

## ขั้นตอนการพัฒนา

1. **POC (Proof of Concept)**:
   - ทดสอบการนำเข้าเอกสาร PMQA ตัวอย่าง 1-2 หมวด
   - สร้างโครงสร้างกราฟเบื้องต้น
   - ทดสอบการ query ด้วย vector search และ graph traversal

2. **การพัฒนาระบบเต็มรูปแบบ**:
   - พัฒนา Document Processing Pipeline
   - พัฒนา Graph Schema และ Query Engine
   - พัฒนา UI สำหรับการจัดการเอกสารและการค้นหา
   - เชื่อมต่อกับ Claude AI

3. **การทดสอบและปรับปรุง**:
   - ทดสอบประสิทธิภาพและความแม่นยำ
   - ปรับแต่งค่าพารามิเตอร์ต่างๆ
   - ออปติไมซ์การใช้ทรัพยากร

## เทคโนโลยีและแนวทางการพัฒนา

- ใช้ open source tools เป็นหลัก
- ใช้ async/await เพื่อจัดการทรัพยากรอย่างมีประสิทธิภาพ
- ใช้ Docker สำหรับจัดการ Neo4j และ Chroma DB
- ออกแบบระบบให้สามารถขยายได้ในอนาคต