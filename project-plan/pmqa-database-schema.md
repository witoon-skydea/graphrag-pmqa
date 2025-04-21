# โครงสร้างฐานข้อมูล PMQA 4.0 สำหรับระบบ GraphRAG

เอกสารนี้อธิบายรายละเอียดของโครงสร้างฐานข้อมูลที่ออกแบบสำหรับจัดเก็บข้อมูลตามเกณฑ์ PMQA 4.0 ในระบบ GraphRAG

## 1. โครงสร้าง PMQA 4.0

PMQA (Public Sector Management Quality Award) 4.0 ประกอบด้วย 7 หมวดหลัก แต่ละหมวดมีหัวข้อย่อยและเกณฑ์การประเมินที่เฉพาะเจาะจง ดังนี้:

### หมวด 1: การนำองค์การ
- 1.1 ระบบการนำองค์การที่สร้างความยั่งยืน
  - 1.1.1 ทิศทางองค์การเพื่อการบรรลุพันธกิจของส่วนราชการ 
  - 1.1.2 การสร้างบรรยากาศและสภาพแวดล้อมที่นำไปสู่ความสำเร็จ
- 1.2 ระบบการกำกับดูแลที่มีประสิทธิภาพและสร้างความโปร่งใส
  - 1.2.1 การป้องกัน ปราบปรามการทุจริตและประพฤติมิชอบ และสร้างความโปร่งใสในการปฏิบัติราชการ
- 1.3 คำนึงถึงผลกระทบต่อสังคมและการมุ่งเน้นให้เกิดผลลัพธ์
  - 1.3.1 การจัดการความเสี่ยงด้านผลกระทบเชิงลบ และความกังวลของสาธารณะต่อการดำเนินการ

### หมวด 2: การวางแผนเชิงยุทธศาสตร์
- 2.1 แผนยุทธศาสตร์ที่ตอบสนองความท้าทายและสร้างนวัตกรรมเพื่อการเปลี่ยนแปลง
  - 2.1.1 แผนยุทธศาสตร์ที่ตอบสนองสภาพแวดล้อมและความเปลี่ยนแปลง
- 2.2 การขับเคลื่อนเป้าหมายยุทธศาสตร์ทั้งระยะสั้นและระยะยาว
  - 2.2.1 การกำหนดเป้าประสงค์และตัวชี้วัด
  - 2.2.2 การจัดทำแผนปฏิบัติการ
- 2.3 การติดตามการเปลี่ยนแปลง การปรับแผน และการรายงานผล
  - 2.3.1 มีการติดตามผลการดำเนินงานตามแผนยุทธศาสตร์
  - 2.3.2 มีการวิเคราะห์คาดการณ์ผลการดำเนินงาน
  - 2.3.3 มีการทบทวนปรับปรุงแผน

### หมวด 3: การให้ความสำคัญกับผู้รับบริการและผู้มีส่วนได้ส่วนเสีย
### หมวด 4: การวัด การวิเคราะห์ และการจัดการความรู้
### หมวด 5: การมุ่งเน้นบุคลากร
### หมวด 6: การมุ่งเน้นระบบปฏิบัติการ
### หมวด 7: ผลลัพธ์การดำเนินการ

## 2. โครงสร้างกราฟใน Neo4j

การออกแบบกราฟสำหรับ PMQA 4.0 ประกอบด้วย Nodes และ Relationships ต่างๆ ดังนี้:

### 2.1 Nodes

#### Category
เก็บข้อมูลเกี่ยวกับหมวดหลักของ PMQA 4.0
```cypher
CREATE (c:Category {
  id: "category_1",
  number: 1,
  name: "การนำองค์การ",
  description: "เกณฑ์ในหมวดการนำองค์การ..."
})
```

#### Subcategory
เก็บข้อมูลเกี่ยวกับหัวข้อย่อยในแต่ละหมวด
```cypher
CREATE (s:Subcategory {
  id: "subcategory_1_1",
  number: "1.1",
  name: "ระบบการนำองค์การที่สร้างความยั่งยืน",
  description: "เกณฑ์ในหัวข้อย่อยเกี่ยวกับระบบการนำองค์การ..."
})
```

#### Criteria
เก็บข้อมูลเกี่ยวกับเกณฑ์การประเมินในแต่ละหัวข้อย่อย
```cypher
CREATE (cr:Criteria {
  id: "criteria_1_1_1",
  number: "1.1.1",
  name: "ทิศทางองค์การเพื่อการบรรลุพันธกิจของส่วนราชการ",
  description: "เกณฑ์เกี่ยวกับทิศทางองค์การ..."
})
```

#### Document
เก็บข้อมูลเกี่ยวกับเอกสารที่นำเข้าสู่ระบบ
```cypher
CREATE (d:Document {
  id: "doc_12345",
  title: "รายงานการวิเคราะห์ปัจจัยภายในและภายนอก",
  path: "/documents/หมวด_1/report_factors_analysis.pdf",
  mimetype: "application/pdf",
  created_at: datetime("2025-05-15T10:30:00"),
  modified_at: datetime("2025-05-15T10:30:00"),
  file_size: 1024000,
  owner: "admin"
})
```

#### Chunk
เก็บข้อมูลเกี่ยวกับส่วนย่อยของเอกสารที่ถูกแบ่ง
```cypher
CREATE (ch:Chunk {
  id: "chunk_6789",
  content: "การวิเคราะห์ปัจจัยภายในพบว่าองค์กรมีจุดแข็งในด้านบุคลากรที่มีความเชี่ยวชาญ...",
  document_id: "doc_12345",
  vector_id: "vec_6789",
  start_idx: 1250,
  end_idx: 1500
})
```

#### Keyword
เก็บข้อมูลคำสำคัญที่สกัดได้จากเอกสาร
```cypher
CREATE (k:Keyword {
  id: "keyword_001",
  word: "ปัจจัยภายใน",
  frequency: 15,
  importance: 0.85
})
```

#### Evidence
เก็บข้อมูลหลักฐานที่สนับสนุนเกณฑ์การประเมิน
```cypher
CREATE (e:Evidence {
  id: "evidence_001",
  name: "หลักฐานการวิเคราะห์ปัจจัยภายในและภายนอก",
  description: "เอกสารแสดงการวิเคราะห์ SWOT ขององค์กร",
  created_at: datetime("2025-05-15T10:30:00")
})
```

### 2.2 Relationships

#### BELONGS_TO
เชื่อมโยงระหว่าง Subcategory กับ Category, Criteria กับ Subcategory
```cypher
CREATE (s:Subcategory {id: "subcategory_1_1"})-[:BELONGS_TO]->(c:Category {id: "category_1"})
CREATE (cr:Criteria {id: "criteria_1_1_1"})-[:BELONGS_TO]->(s:Subcategory {id: "subcategory_1_1"})
```

#### HAS_DOCUMENT
เชื่อมโยงระหว่าง Category, Subcategory, หรือ Criteria กับ Document
```cypher
CREATE (c:Category {id: "category_1"})-[:HAS_DOCUMENT]->(d:Document {id: "doc_12345"})
CREATE (cr:Criteria {id: "criteria_1_1_1"})-[:HAS_DOCUMENT {relevance: 0.92}]->(d:Document {id: "doc_12345"})
```

#### HAS_CHUNK
เชื่อมโยงระหว่าง Document กับ Chunk
```cypher
CREATE (d:Document {id: "doc_12345"})-[:HAS_CHUNK]->(ch:Chunk {id: "chunk_6789"})
```

#### RELATES_TO
เชื่อมโยงระหว่าง Document กับ Document ที่มีความเกี่ยวข้องกัน
```cypher
CREATE (d1:Document {id: "doc_12345"})-[:RELATES_TO {strength: 0.75}]->(d2:Document {id: "doc_67890"})
```

#### MENTIONS
เชื่อมโยงระหว่าง Chunk กับ Keyword
```cypher
CREATE (ch:Chunk {id: "chunk_6789"})-[:MENTIONS {count: 3}]->(k:Keyword {id: "keyword_001"})
```

#### SUPPORTS
เชื่อมโยงระหว่าง Evidence กับ Criteria
```cypher
CREATE (e:Evidence {id: "evidence_001"})-[:SUPPORTS {strength: 0.9}]->(cr:Criteria {id: "criteria_1_1_1"})
```

## 3. การจัดเก็บ Embeddings ใน Chroma DB

Chroma DB จะเก็บ embeddings ของเอกสารและชิ้นส่วนเอกสาร โดยมีโครงสร้างดังนี้:

### 3.1 Collections

#### documents
เก็บ embeddings ของเอกสารทั้งฉบับ

```python
documents_collection = client.create_collection(
    name="documents",
    metadata={
        "description": "Embeddings of complete documents"
    }
)

documents_collection.add(
    ids=["doc_12345"],
    embeddings=[...],  # vector representation
    documents=["รายงานการวิเคราะห์ปัจจัยภายในและภายนอก..."],
    metadatas=[{
        "title": "รายงานการวิเคราะห์ปัจจัยภายในและภายนอก",
        "category": "หมวด_1",
        "subcategory": "1.1",
        "criteria": "1.1.1",
        "path": "/documents/หมวด_1/report_factors_analysis.pdf",
        "mimetype": "application/pdf",
        "created_at": "2025-05-15T10:30:00"
    }]
)
```

#### chunks
เก็บ embeddings ของชิ้นส่วนเอกสาร

```python
chunks_collection = client.create_collection(
    name="chunks",
    metadata={
        "description": "Embeddings of document chunks"
    }
)

chunks_collection.add(
    ids=["chunk_6789"],
    embeddings=[...],  # vector representation
    documents=["การวิเคราะห์ปัจจัยภายในพบว่าองค์กรมีจุดแข็งในด้านบุคลากรที่มีความเชี่ยวชาญ..."],
    metadatas=[{
        "document_id": "doc_12345",
        "title": "รายงานการวิเคราะห์ปัจจัยภายในและภายนอก",
        "category": "หมวด_1",
        "subcategory": "1.1",
        "criteria": "1.1.1",
        "start_idx": 1250,
        "end_idx": 1500
    }]
)
```

### 3.2 การค้นหา

```python
# ค้นหาชิ้นส่วนเอกสารที่เกี่ยวข้องกับคำค้นหา
results = chunks_collection.query(
    query_texts=["การวิเคราะห์ปัจจัยภายในและภายนอกขององค์กร"],
    n_results=5,
    where={"category": "หมวด_1"}
)
```

## 4. การจัดเก็บเอกสารใน Filesystem

ระบบจะจัดเก็บเอกสารต้นฉบับในโครงสร้างโฟลเดอร์ที่สอดคล้องกับ PMQA 4.0 ดังนี้:

```
/documents/
├── หมวด_1/
│   ├── 1.1_ระบบการนำองค์การ/
│   │   ├── 1.1.1_ทิศทางองค์การ/
│   │   │   ├── report_factors_analysis.pdf
│   │   │   └── strategic_plan.docx
│   │   └── 1.1.2_การสร้างบรรยากาศ/
│   ├── 1.2_ระบบการกำกับดูแล/
│   └── 1.3_ผลกระทบต่อสังคม/
├── หมวด_2/
│   └── ...
├── หมวด_3/
│   └── ...
├── หมวด_4/
│   └── ...
├── หมวด_5/
│   └── ...
├── หมวด_6/
│   └── ...
├── หมวด_7/
│   └── ...
└── raw/
    ├── incoming_doc_1.pdf
    ├── incoming_doc_2.docx
    └── ...
```

## 5. การจัดเก็บโครงสร้าง PMQA ใน JSON

เพื่อความสะดวกในการสร้างและจัดการโครงสร้าง PMQA 4.0 ระบบจะใช้ไฟล์ JSON เป็นแหล่งข้อมูลหลัก:

```json
{
  "categories": [
    {
      "id": "category_1",
      "number": 1,
      "name": "การนำองค์การ",
      "description": "เกณฑ์ในหมวดการนำองค์การ...",
      "subcategories": [
        {
          "id": "subcategory_1_1",
          "number": "1.1",
          "name": "ระบบการนำองค์การที่สร้างความยั่งยืน",
          "description": "เกณฑ์ในหัวข้อย่อยเกี่ยวกับระบบการนำองค์การ...",
          "criteria": [
            {
              "id": "criteria_1_1_1",
              "number": "1.1.1",
              "name": "ทิศทางองค์การเพื่อการบรรลุพันธกิจของส่วนราชการ",
              "description": "เกณฑ์เกี่ยวกับทิศทางองค์การ...",
              "points": [
                "1) วิเคราะห์ปัจจัยภายในและปัจจัยภายนอกที่ส่งผลกระทบกับองค์การ",
                "2) วิเคราะห์และระบุความท้าทายและความเสี่ยงที่สำคัญขององค์การ",
                "3) วิเคราะห์และสำรวจบริบทความเปลี่ยนแปลงในอนาคตที่สำคัญ",
                "4) ทิศทางองค์การตอบสนองครอบคลุมต่อประเด็นต่าง ๆ",
                "5) ทิศทางองค์การตอบสนองต่อการสร้างการเปลี่ยนแปลงที่มีผลกระทบสูง"
              ]
            },
            {
              "id": "criteria_1_1_2",
              "number": "1.1.2",
              "name": "การสร้างบรรยากาศและสภาพแวดล้อมที่นำไปสู่ความสำเร็จ",
              "description": "เกณฑ์เกี่ยวกับการสร้างบรรยากาศ...",
              "points": [
                "1) สื่อสารถ่ายทอดนโยบายไปยังผู้ที่มีส่วนเกี่ยวข้อง",
                "2) ผู้ที่เกี่ยวข้องมีส่วนร่วมในการกำหนดทิศทาง",
                "3) มีการจัดทำแผนงานบูรณาการร่วมกัน"
              ]
            }
          ]
        },
        // และอื่นๆ
      ]
    },
    // หมวดอื่นๆ
  ]
}
```

## 6. ตัวอย่าง Cypher Queries สำหรับการค้นหาข้อมูล

### 6.1 ค้นหาเอกสารที่เกี่ยวข้องกับหมวดหนึ่ง
```cypher
MATCH (d:Document)-[:HAS_DOCUMENT]-(c:Category {number: 1})
RETURN d.title, d.path, d.created_at
ORDER BY d.created_at DESC
LIMIT 10
```

### 6.2 ค้นหาเอกสารที่เกี่ยวข้องกับเกณฑ์เฉพาะ
```cypher
MATCH (d:Document)-[:HAS_DOCUMENT]-(cr:Criteria {number: "1.1.1"})
RETURN d.title, d.path, d.created_at
ORDER BY d.created_at DESC
LIMIT 10
```

### 6.3 ค้นหาชิ้นส่วนเอกสารที่มีคำสำคัญเฉพาะ
```cypher
MATCH (ch:Chunk)-[:MENTIONS]-(k:Keyword {word: "ปัจจัยภายใน"})
MATCH (ch)-[:HAS_CHUNK]-(d:Document)
RETURN ch.content, d.title, d.path
LIMIT 10
```

### 6.4 ค้นหาเอกสารที่เกี่ยวข้องกันตามความสัมพันธ์
```cypher
MATCH (d1:Document {id: "doc_12345"})-[:RELATES_TO]-(d2:Document)
RETURN d2.title, d2.path
ORDER BY d2.created_at DESC
LIMIT 10
```

### 6.5 ค้นหาหลักฐานที่สนับสนุนเกณฑ์เฉพาะ
```cypher
MATCH (e:Evidence)-[:SUPPORTS]-(cr:Criteria {number: "1.1.1"})
RETURN e.name, e.description, e.created_at
ORDER BY e.created_at DESC
LIMIT 10
```

## 7. โครงสร้างข้อมูลสำหรับการส่งข้อมูลให้ Claude AI

เมื่อต้องการส่งข้อมูลไปยัง Claude AI เพื่อตอบคำถามเกี่ยวกับ PMQA จะใช้โครงสร้างดังนี้:

```json
{
  "query": "อธิบายวิธีการวิเคราะห์ปัจจัยภายในและภายนอกตามเกณฑ์ PMQA หมวด 1.1.1",
  "context": [
    {
      "content": "การวิเคราะห์ปัจจัยภายในพบว่าองค์กรมีจุดแข็งในด้านบุคลากรที่มีความเชี่ยวชาญ...",
      "document": "รายงานการวิเคราะห์ปัจจัยภายในและภายนอก",
      "path": "/documents/หมวด_1/report_factors_analysis.pdf",
      "category": "1",
      "subcategory": "1.1",
      "criteria": "1.1.1"
    },
    {
      "content": "การวิเคราะห์ปัจจัยภายนอกควรพิจารณาปัจจัยด้านการเมือง เศรษฐกิจ สังคม เทคโนโลยี...",
      "document": "คู่มือการวิเคราะห์ SWOT",
      "path": "/documents/หมวด_1/swot_analysis_guide.docx",
      "category": "1",
      "subcategory": "1.1",
      "criteria": "1.1.1"
    }
  ],
  "criteria_info": {
    "number": "1.1.1",
    "name": "ทิศทางองค์การเพื่อการบรรลุพันธกิจของส่วนราชการ",
    "points": [
      "1) วิเคราะห์ปัจจัยภายในและปัจจัยภายนอกที่ส่งผลกระทบกับองค์การ",
      "2) วิเคราะห์และระบุความท้าทายและความเสี่ยงที่สำคัญขององค์การ"
    ]
  }
}
```

## 8. การขยายโครงสร้างในอนาคต

โครงสร้างฐานข้อมูลนี้ออกแบบให้สามารถขยายเพิ่มเติมได้ในอนาคต เช่น:

1. เพิ่ม Node สำหรับ User เพื่อจัดการสิทธิ์ในการเข้าถึงข้อมูล
2. เพิ่ม Node สำหรับ Organization เพื่อรองรับการใช้งานแบบหลายองค์กร
3. เพิ่ม Relationship ประเภท PREREQUISITE_FOR เพื่อแสดงความสัมพันธ์ระหว่างเกณฑ์
4. เพิ่ม Node สำหรับ Project เพื่อติดตามโครงการที่เกี่ยวข้องกับการพัฒนาตามเกณฑ์ PMQA