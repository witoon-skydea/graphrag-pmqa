import streamlit as st
import requests

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

def render():
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
