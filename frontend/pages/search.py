import streamlit as st
import requests

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

def render():
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
