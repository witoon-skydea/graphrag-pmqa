import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
import pandas as pd
import io

# Set page configuration
st.set_page_config(
    page_title="GraphRAG PMQA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

# CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .stat-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        flex: 1;
        min-width: 200px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #616161;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        font-size: 0.8rem;
        color: #9e9e9e;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar navigation
    st.sidebar.markdown("# GraphRAG PMQA")
    st.sidebar.markdown("---")
    
    # Navigation options
    pages = {
        "หน้าหลัก": home_page,
        "อัปโหลดเอกสาร": upload_page,
        "จัดการเอกสาร": documents_page,
        "ค้นหาข้อมูล": search_page,
        "ถาม-ตอบกับ Claude AI": chat_page,
        "โครงสร้าง PMQA": pmqa_structure_page,
        "สถานะระบบ": system_status_page
    }
    
    selection = st.sidebar.radio("เมนู", list(pages.keys()))
    
    # Display the selected page
    pages[selection]()
    
    # Footer
    st.markdown("""
    <div class="footer">
        GraphRAG for PMQA 4.0 © 2025
    </div>
    """, unsafe_allow_html=True)

def home_page():
    # Header
    st.markdown('<div class="main-header">GraphRAG for PMQA 4.0</div>', unsafe_allow_html=True)
    st.markdown("""
    ระบบจัดการและค้นหาข้อมูลตามโครงสร้าง PMQA 4.0 (Public Sector Management Quality Award) 
    โดยเน้นการใช้ Graph Database และ Vector Search เพื่อเพิ่มประสิทธิภาพในการค้นหาและเรียกใช้ข้อมูลที่เกี่ยวข้อง
    """)
    
    # System statistics
    st.markdown('<div class="sub-header">ภาพรวมระบบ</div>', unsafe_allow_html=True)
    
    # Try to get document count
    try:
        response = requests.get(f"{API_BASE_URL}/documents?limit=1")
        if response.status_code == 200:
            doc_count = response.json().get("total", 0)
        else:
            doc_count = "N/A"
    except:
        doc_count = "N/A"
    
    # Mock data for demonstration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">เอกสารทั้งหมด</div>
        </div>
        """.format(doc_count), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">7</div>
            <div class="stat-label">หมวด PMQA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">14</div>
            <div class="stat-label">หัวข้อย่อย</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">28</div>
            <div class="stat-label">เกณฑ์การประเมิน</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature cards
    st.markdown('<div class="sub-header">ฟังก์ชั่นการทำงาน</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📤 อัปโหลดและจัดหมวดหมู่เอกสาร</h3>
            <p>อัปโหลดเอกสารเข้าสู่ระบบและจัดหมวดหมู่ตามโครงสร้าง PMQA 4.0 โดยอัตโนมัติ</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("ไปที่การอัปโหลดเอกสาร", key="upload_btn"):
            st.switch_page("app.py")  # This will reload the page with the upload_page query param
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🔍 ค้นหาข้อมูลอัจฉริยะ</h3>
            <p>ค้นหาข้อมูลโดยใช้ Vector Search และ Graph Database เพื่อเพิ่มประสิทธิภาพในการค้นหา</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("ไปที่การค้นหา", key="search_btn"):
            st.switch_page("app.py")  # This will reload the page with the search_page query param
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>💬 ถาม-ตอบกับ Claude AI</h3>
            <p>ถามคำถามเกี่ยวกับ PMQA 4.0 และได้รับคำตอบจาก Claude AI พร้อมแหล่งอ้างอิง</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("ไปที่การถาม-ตอบ", key="chat_btn"):
            st.switch_page("app.py")  # This will reload the page with the chat_page query param
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>📊 โครงสร้าง PMQA</h3>
            <p>ดูโครงสร้าง PMQA 4.0 ทั้งหมด พร้อมรายละเอียดและความสัมพันธ์</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("ไปที่โครงสร้าง PMQA", key="pmqa_btn"):
            st.switch_page("app.py")  # This will reload the page with the pmqa_structure_page query param

def upload_page():
    st.markdown('<div class="main-header">อัปโหลดเอกสาร</div>', unsafe_allow_html=True)
    st.markdown("อัปโหลดเอกสารเข้าสู่ระบบ โดยระบบจะวิเคราะห์และจัดหมวดหมู่ตามโครงสร้าง PMQA 4.0 โดยอัตโนมัติ")
    
    with st.form("upload_form"):
        uploaded_file = st.file_uploader("เลือกไฟล์เอกสาร", type=["pdf", "docx", "doc", "txt", "md"])
        title = st.text_input("ชื่อเอกสาร (ไม่บังคับ)")
        description = st.text_area("คำอธิบาย (ไม่บังคับ)")
        author = st.text_input("ผู้เขียน/หน่วยงาน (ไม่บังคับ)")
        
        # PMQA Categories for selection
        categories = [
            "หมวด_1", "หมวด_2", "หมวด_3", 
            "หมวด_4", "หมวด_5", "หมวด_6", "หมวด_7"
        ]
        category = st.selectbox("หมวด PMQA (ไม่บังคับ)", [""] + categories)
        
        tags = st.text_input("แท็ก (คั่นด้วยเครื่องหมายคอมม่า, ไม่บังคับ)")
        
        submit_button = st.form_submit_button("อัปโหลด")
    
    if submit_button and uploaded_file is not None:
        # Display a spinner while uploading
        with st.spinner("กำลังอัปโหลดและประมวลผลเอกสาร..."):
            try:
                # Create form data
                form_data = {
                    "title": title if title else None,
                    "description": description if description else None,
                    "author": author if author else None,
                    "category": category if category else None,
                    "tags": tags if tags else None
                }
                
                # Remove None values
                form_data = {k: v for k, v in form_data.items() if v is not None}
                
                # Prepare the file
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Send to API
                response = requests.post(
                    f"{API_BASE_URL}/documents",
                    files=files,
                    data=form_data
                )
                
                if response.status_code == 202:
                    document_id = response.json().get("document_id")
                    st.success(f"อัปโหลดเอกสารสำเร็จ! กำลังประมวลผล... (ID: {document_id})")
                    
                    # Display processing status
                    if document_id:
                        st.info("สถานะการประมวลผล:")
                        status_placeholder = st.empty()
                        progress_bar = st.progress(0)
                        
                        # Poll for status updates
                        complete = False
                        retry_count = 0
                        
                        while not complete and retry_count < 30:  # Timeout after 30 tries
                            try:
                                status_response = requests.get(f"{API_BASE_URL}/documents/{document_id}/status")
                                
                                if status_response.status_code == 200:
                                    status_data = status_response.json()
                                    status = status_data.get("status", "unknown")
                                    progress = status_data.get("progress", 0)
                                    
                                    # Update UI
                                    status_placeholder.text(f"สถานะ: {status}, ความคืบหน้า: {progress}%")
                                    progress_bar.progress(progress / 100)
                                    
                                    if status == "completed":
                                        complete = True
                                        st.success("ประมวลผลเอกสารเสร็จสิ้น!")
                                        break
                                    elif status == "failed":
                                        st.error(f"ประมวลผลเอกสารล้มเหลว: {status_data.get('error', 'ไม่ทราบสาเหตุ')}")
                                        break
                                
                                time.sleep(1)  # Wait for 1 second before polling again
                                retry_count += 1
                                
                            except Exception as e:
                                st.error(f"เกิดข้อผิดพลาดในการติดตามสถานะ: {str(e)}")
                                break
                        
                        if not complete and retry_count >= 30:
                            st.warning("หมดเวลาการติดตามสถานะ แต่เอกสารยังคงประมวลผลในเบื้องหลัง")
                else:
                    st.error(f"อัปโหลดเอกสารล้มเหลว: {response.json().get('detail', 'ไม่ทราบสาเหตุ')}")
            
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def documents_page():
    st.markdown('<div class="main-header">จัดการเอกสาร</div>', unsafe_allow_html=True)
    st.markdown("จัดการเอกสารที่อัปโหลดเข้าสู่ระบบ")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "กรองตามหมวด",
            ["", "หมวด_1", "หมวด_2", "หมวด_3", "หมวด_4", "หมวด_5", "หมวด_6", "หมวด_7", "raw"]
        )
    
    with col2:
        author_filter = st.text_input("กรองตามผู้เขียน/หน่วยงาน")
    
    with col3:
        keyword_filter = st.text_input("กรองตามคำค้นหา")
    
    # Apply button
    if st.button("ค้นหาเอกสาร"):
        # Build query parameters
        params = {}
        if category_filter:
            params["category"] = category_filter
        if author_filter:
            params["author"] = author_filter
        if keyword_filter:
            params["keyword"] = keyword_filter
        
        # Fetch documents
        try:
            response = requests.get(f"{API_BASE_URL}/documents", params=params)
            
            if response.status_code == 200:
                documents_data = response.json()
                documents = documents_data.get("documents", [])
                total = documents_data.get("total", 0)
                
                # Display results
                st.success(f"พบ {total} เอกสาร")
                
                if documents:
                    # Create a DataFrame for display
                    df_data = []
                    
                    for doc in documents:
                        # Format datetime
                        created_at = datetime.fromisoformat(doc.get("created_at")) if "created_at" in doc else None
                        created_str = created_at.strftime("%d/%m/%Y %H:%M") if created_at else "N/A"
                        
                        # Format category
                        category = doc.get("category", "N/A")
                        
                        # Status indicator
                        processed = "✅" if doc.get("processed", False) else "⏳"
                        
                        df_data.append({
                            "ID": doc.get("id", ""),
                            "ชื่อเอกสาร": doc.get("title", "ไม่มีชื่อ"),
                            "หมวด": category,
                            "ผู้เขียน/หน่วยงาน": doc.get("author", ""),
                            "วันที่สร้าง": created_str,
                            "ประมวลผล": processed,
                            "ขนาด (bytes)": doc.get("size", 0)
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Select a document for more details
                    st.markdown("### รายละเอียดเอกสาร")
                    doc_id = st.selectbox("เลือกเอกสารเพื่อดูรายละเอียด", [doc.get("id", "") for doc in documents])
                    
                    if doc_id:
                        # Find the selected document
                        selected_doc = next((doc for doc in documents if doc.get("id", "") == doc_id), None)
                        
                        if selected_doc:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**ชื่อเอกสาร:** {selected_doc.get('title', 'ไม่มีชื่อ')}")
                                st.markdown(f"**คำอธิบาย:** {selected_doc.get('description', '-')}")
                                st.markdown(f"**ผู้เขียน/หน่วยงาน:** {selected_doc.get('author', '-')}")
                                st.markdown(f"**หมวด:** {selected_doc.get('category', '-')}")
                                
                                if 'pmqa_references' in selected_doc and selected_doc['pmqa_references']:
                                    st.markdown("**อ้างอิง PMQA:**")
                                    for ref in selected_doc['pmqa_references']:
                                        st.markdown(f"- {ref.get('category_name', '')} ({ref.get('category_id', '')})")
                            
                            with col2:
                                download_url = selected_doc.get("download_url", "")
                                if download_url:
                                    download_link = f"{API_BASE_URL}{download_url.lstrip('/')}"
                                    st.markdown(f"[📥 ดาวน์โหลดเอกสาร]({download_link})")
                                
                                st.markdown(f"**ประมวลผล:** {'เสร็จสิ้น' if selected_doc.get('processed', False) else 'กำลังดำเนินการ'}")
                                st.markdown(f"**ขนาดไฟล์:** {selected_doc.get('size', 0):,} bytes")
                                
                                if 'keywords' in selected_doc and selected_doc['keywords']:
                                    st.markdown("**คำสำคัญ:**")
                                    st.write(", ".join(selected_doc['keywords']))
                else:
                    st.info("ไม่พบเอกสาร")
            else:
                st.error(f"ไม่สามารถโหลดเอกสารได้: {response.json().get('detail', 'ไม่ทราบสาเหตุ')}")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def search_page():
    st.markdown('<div class="main-header">ค้นหาข้อมูล</div>', unsafe_allow_html=True)
    st.markdown("ค้นหาข้อมูลในเอกสารโดยใช้ Vector Search และ Graph Search")
    
    # Search options
    search_query = st.text_input("คำค้นหา", placeholder="ค้นหาในเอกสาร...")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_type = st.selectbox(
            "ประเภทการค้นหา",
            ["hybrid", "vector", "graph"],
            format_func=lambda x: {
                "hybrid": "Hybrid Search (ผสม)",
                "vector": "Vector Search (ค้นหาความคล้ายคลึง)",
                "graph": "Graph Search (ค้นหาความสัมพันธ์)"
            }.get(x, x)
        )
    
    with col2:
        category_filter = st.selectbox(
            "กรองตามหมวด",
            ["", "หมวด_1", "หมวด_2", "หมวด_3", "หมวด_4", "หมวด_5", "หมวด_6", "หมวด_7"]
        )
    
    with col3:
        top_k = st.slider("จำนวนผลลัพธ์", min_value=1, max_value=20, value=5)
    
    # Advanced options
    with st.expander("ตัวเลือกขั้นสูง"):
        if search_type == "hybrid":
            col1, col2 = st.columns(2)
            with col1:
                vector_weight = st.slider("น้ำหนัก Vector Search", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            with col2:
                graph_weight = st.slider("น้ำหนัก Graph Search", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        
        pmqa_category = st.selectbox("หมวด PMQA สำหรับการค้นหาแบบ Graph", [""] + [str(i) for i in range(1, 8)])
        pmqa_subcategory = st.text_input("หัวข้อย่อย PMQA (เช่น 1.1)")
    
    # Search button
    if st.button("ค้นหา") and search_query:
        with st.spinner("กำลังค้นหา..."):
            try:
                # Build search request
                search_request = {
                    "query": search_query,
                    "filters": {}
                }
                
                # Add filters
                if category_filter:
                    search_request["filters"]["category"] = category_filter
                
                # Add PMQA reference for graph or hybrid search
                if (search_type in ["graph", "hybrid"]) and (pmqa_category or pmqa_subcategory):
                    pmqa_reference = {}
                    if pmqa_category:
                        pmqa_reference["category_id"] = pmqa_category
                    if pmqa_subcategory:
                        pmqa_reference["subcategory_id"] = pmqa_subcategory
                    
                    if pmqa_reference:
                        search_request["pmqa_reference"] = pmqa_reference
                
                # Add search type specific parameters
                if search_type == "vector":
                    search_request["top_k"] = top_k
                    search_url = f"{API_BASE_URL}/search/vector"
                
                elif search_type == "graph":
                    search_url = f"{API_BASE_URL}/search/graph"
                
                elif search_type == "hybrid":
                    search_request["top_k"] = top_k
                    search_request["vector_weight"] = vector_weight
                    search_request["graph_weight"] = graph_weight
                    search_url = f"{API_BASE_URL}/search/hybrid"
                
                # Execute search
                response = requests.post(search_url, json=search_request)
                
                if response.status_code == 200:
                    results = response.json()
                    search_results = results.get("results", [])
                    total_results = results.get("total_results", 0)
                    execution_time = results.get("execution_time_ms", 0)
                    
                    # Display results
                    st.success(f"พบ {total_results} ผลลัพธ์ (ใช้เวลา {execution_time:.2f} ms)")
                    
                    if search_results:
                        # Create tabs for different result views
                        tab1, tab2 = st.tabs(["รายการผลลัพธ์", "แสดงรายละเอียด"])
                        
                        with tab1:
                            for i, result in enumerate(search_results):
                                with st.container():
                                    st.markdown(
                                        f"""
                                        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                                            <h4>{i+1}. {result.get('document_title', 'ไม่มีชื่อ')}</h4>
                                            <p><strong>ความเกี่ยวข้อง:</strong> {result.get('score', 0):.2f}</p>
                                            <p>{result.get('content', '')[:300]}...</p>
                                            <p><strong>PMQA:</strong> {', '.join([f"{ref.get('category_name', '')} ({ref.get('category_id', '')})" for ref in result.get('pmqa_references', [])])}</p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                        
                        with tab2:
                            # Select a result to view in detail
                            selected_idx = st.selectbox(
                                "เลือกผลลัพธ์เพื่อดูรายละเอียด",
                                range(len(search_results)),
                                format_func=lambda i: f"{i+1}. {search_results[i].get('document_title', 'ไม่มีชื่อ')}"
                            )
                            
                            # Display selected result
                            if selected_idx is not None:
                                selected_result = search_results[selected_idx]
                                
                                st.markdown(f"### {selected_result.get('document_title', 'ไม่มีชื่อ')}")
                                st.markdown(f"**Document ID:** {selected_result.get('document_id', '')}")
                                st.markdown(f"**Chunk ID:** {selected_result.get('chunk_id', '')}")
                                st.markdown(f"**ความเกี่ยวข้อง:** {selected_result.get('score', 0):.2f}")
                                
                                st.markdown("### เนื้อหา:")
                                st.markdown(selected_result.get('content', ''))
                                
                                st.markdown("### อ้างอิง PMQA:")
                                if 'pmqa_references' in selected_result and selected_result['pmqa_references']:
                                    for ref in selected_result['pmqa_references']:
                                        st.markdown(
                                            f"- {ref.get('category_name', '')} ({ref.get('category_id', '')})"
                                            + (f" > {ref.get('subcategory_name', '')} ({ref.get('subcategory_id', '')})" if 'subcategory_name' in ref else "")
                                            + (f" > {ref.get('criteria_name', '')} ({ref.get('criteria_id', '')})" if 'criteria_name' in ref else "")
                                        )
                                else:
                                    st.markdown("ไม่มีข้อมูลอ้างอิง PMQA")
                                
                                # Metadata
                                if 'metadata' in selected_result:
                                    st.markdown("### ข้อมูลเพิ่มเติม:")
                                    for key, value in selected_result['metadata'].items():
                                        st.markdown(f"**{key}:** {value}")
                    else:
                        st.info("ไม่พบผลลัพธ์")
                else:
                    st.error(f"ค้นหาล้มเหลว: {response.json().get('detail', 'ไม่ทราบสาเหตุ')}")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def chat_page():
    st.markdown('<div class="main-header">ถาม-ตอบกับ Claude AI</div>', unsafe_allow_html=True)
    st.markdown("ถามคำถามเกี่ยวกับ PMQA 4.0 และได้รับคำตอบจาก Claude AI พร้อมแหล่งอ้างอิง")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if "sources" in message and message["sources"]:
                with st.expander("แหล่งข้อมูลอ้างอิง"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(
                            f"**[{i+1}] จากเอกสาร:** {source.get('document_title', 'ไม่ระบุ')}"
                        )
                        st.markdown(f"*ข้อความ:* {source.get('content_snippet', '')}")
    
    # Chat options
    with st.expander("ตัวเลือกการถาม-ตอบ"):
        col1, col2 = st.columns(2)
        
        with col1:
            use_rag = st.checkbox("ใช้ข้อมูลจากเอกสาร (RAG)", value=True)
            search_type = st.selectbox(
                "ประเภทการค้นหา",
                ["hybrid", "vector", "graph"],
                format_func=lambda x: {
                    "hybrid": "Hybrid Search (ผสม)",
                    "vector": "Vector Search (ค้นหาความคล้ายคลึง)",
                    "graph": "Graph Search (ค้นหาความสัมพันธ์)"
                }.get(x, x)
            )
        
        with col2:
            pmqa_category = st.selectbox("หมวด PMQA", [""] + [str(i) for i in range(1, 8)])
            pmqa_subcategory = st.text_input("หัวข้อย่อย PMQA (เช่น 1.1)")
            max_tokens = st.slider("ความยาวคำตอบสูงสุด", 100, 3000, 1000)
    
    # Chat input
    query = st.chat_input("ถามคำถามเกี่ยวกับ PMQA 4.0...")
    
    if query:
        # Display user message
        with st.chat_message("user"):
            st.markdown(query)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Process with Claude
        with st.chat_message("assistant"):
            with st.spinner("กำลังคิด..."):
                try:
                    # Build Claude query
                    claude_request = {
                        "query": query,
                        "use_rag": use_rag,
                        "search_type": search_type,
                        "max_tokens": max_tokens
                    }
                    
                    # Add PMQA reference if available
                    if pmqa_category or pmqa_subcategory:
                        pmqa_reference = {}
                        if pmqa_category:
                            pmqa_reference["category_id"] = pmqa_category
                        if pmqa_subcategory:
                            pmqa_reference["subcategory_id"] = pmqa_subcategory
                        
                        claude_request["pmqa_reference"] = pmqa_reference
                    
                    # Call Claude API
                    response = requests.post(f"{API_BASE_URL}/claude/query", json=claude_request)
                    
                    if response.status_code == 200:
                        claude_response = response.json()
                        answer = claude_response.get("answer", "ขออภัย ฉันไม่สามารถตอบคำถามนี้ได้")
                        sources = claude_response.get("sources", [])
                        
                        # Display answer
                        st.markdown(answer)
                        
                        # Display sources
                        if sources:
                            with st.expander("แหล่งข้อมูลอ้างอิง"):
                                for i, source in enumerate(sources):
                                    st.markdown(
                                        f"**[{i+1}] จากเอกสาร:** {source.get('document_title', 'ไม่ระบุ')}"
                                    )
                                    st.markdown(f"*ข้อความ:* {source.get('content_snippet', '')}")
                        
                        # Add assistant message to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        st.error(f"ไม่สามารถติดต่อ Claude AI ได้: {response.json().get('detail', 'ไม่ทราบสาเหตุ')}")
                
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def pmqa_structure_page():
    st.markdown('<div class="main-header">โครงสร้าง PMQA 4.0</div>', unsafe_allow_html=True)
    st.markdown("ดูโครงสร้าง PMQA 4.0 ทั้งหมด พร้อมรายละเอียดและความสัมพันธ์")
    
    try:
        # Fetch PMQA structure
        response = requests.get(f"{API_BASE_URL}/pmqa/structure")
        
        if response.status_code == 200:
            pmqa_data = response.json()
            categories = pmqa_data.get("categories", [])
            
            # Display structure as tabs
            category_tabs = st.tabs([f"หมวด {cat['id']}" for cat in categories])
            
            for i, category in enumerate(categories):
                with category_tabs[i]:
                    st.markdown(f"## {category['name']} (หมวด {category['id']})")
                    st.markdown(f"*{category['description']}*")
                    
                    # Subcategories
                    subcategories = category.get("subcategories", [])
                    
                    if subcategories:
                        for subcategory in subcategories:
                            st.markdown(f"### {subcategory['id']} {subcategory['name']}")
                            st.markdown(f"*{subcategory['description']}*")
                            
                            # Criteria
                            criteria = subcategory.get("criteria", [])
                            
                            if criteria:
                                for criterion in criteria:
                                    st.markdown(f"#### {criterion['id']} {criterion['name']}")
                                    st.markdown(f"*{criterion['description']}*")
                            else:
                                st.info(f"ไม่มีเกณฑ์ในหัวข้อย่อย {subcategory['id']}")
                    else:
                        st.info(f"ไม่มีหัวข้อย่อยในหมวด {category['id']}")
        else:
            st.error(f"ไม่สามารถโหลดโครงสร้าง PMQA ได้: {response.json().get('detail', 'ไม่ทราบสาเหตุ')}")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def system_status_page():
    st.markdown('<div class="main-header">สถานะระบบ</div>', unsafe_allow_html=True)
    st.markdown("ตรวจสอบสถานะการทำงานของระบบและบริการที่เกี่ยวข้อง")
    
    try:
        # Check API health
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            overall_status = health_data.get("status", "unknown")
            services = health_data.get("services", {})
            
            # Overall status
            if overall_status == "healthy":
                st.success("ระบบทำงานปกติ")
            else:
                st.error("ระบบมีปัญหาบางส่วน")
            
            # Services status
            st.markdown("### สถานะบริการ")
            
            # Create DataFrame for services
            df_data = []
            
            for service, status in services.items():
                icon = "✅" if status == "healthy" else "❌"
                df_data.append({
                    "บริการ": service,
                    "สถานะ": f"{icon} {status}"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # System information
            st.markdown("### ข้อมูลระบบ")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**API Version:** 1.0.0")
                st.markdown("**GraphRAG Version:** 1.0.0")
                st.markdown("**Claude AI:** Enabled")
            
            with col2:
                st.markdown("**Neo4j:** " + ("Connected" if services.get("neo4j") == "healthy" else "Not Connected"))
                st.markdown("**Chroma DB:** " + ("Connected" if services.get("chroma") == "healthy" else "Not Connected"))
                st.markdown("**Ollama:** Available")
        else:
            st.error(f"ไม่สามารถตรวจสอบสถานะระบบได้: {response.status_code}")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    main()
