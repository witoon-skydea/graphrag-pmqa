import streamlit as st
import requests
import time

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

def render():
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
