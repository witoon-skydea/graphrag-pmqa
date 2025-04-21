#!/bin/bash

# GraphRAG for PMQA 4.0 - Test Runner Script
# สคริปต์นี้ใช้สำหรับรันชุดทดสอบต่างๆ สำหรับ GraphRAG PMQA 4.0

echo "============================================"
echo "GraphRAG for PMQA 4.0 - Test Runner"
echo "============================================"

PROJECT_DIR="/Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1"
TEST_DIR="/Users/witoonpongsilathong/MCP_folder/mm_dev_mode/hope_x1/tests"

# ตรวจสอบว่าสภาพแวดล้อมพร้อมสำหรับการทดสอบหรือไม่
check_environment() {
    echo "ตรวจสอบสภาพแวดล้อมการทดสอบ..."
    
    # ตรวจสอบว่า Docker และ Docker Compose ติดตั้งแล้ว
    if ! command -v docker &> /dev/null; then
        echo "❌ ไม่พบ Docker - กรุณาติดตั้ง Docker ก่อนดำเนินการต่อ"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ ไม่พบ Docker Compose - กรุณาติดตั้ง Docker Compose ก่อนดำเนินการต่อ"
        exit 1
    fi
    
    # ตรวจสอบว่า pytest ติดตั้งแล้ว
    if ! command -v pytest &> /dev/null; then
        echo "❌ ไม่พบ pytest - กำลังติดตั้ง..."
        pip install pytest pytest-cov pytest-asyncio httpx pytest-mock
    fi
    
    echo "✅ สภาพแวดล้อมพร้อมสำหรับการทดสอบ"
}

# เตรียมโครงสร้างไดเรกทอรีสำหรับการทดสอบ
prepare_test_directory() {
    echo "เตรียมโครงสร้างไดเรกทอรีสำหรับการทดสอบ..."
    
    # สร้างโครงสร้างไดเรกทอรีการทดสอบหากยังไม่มี
    mkdir -p ${TEST_DIR}/{unit,integration,system,performance,usability}
    mkdir -p ${TEST_DIR}/unit/{test_api,test_db,test_models,test_services,test_utils}
    mkdir -p ${TEST_DIR}/performance/sample_files
    
    echo "✅ โครงสร้างไดเรกทอรีพร้อมแล้ว"
}

# คัดลอกไฟล์ทดสอบจาก project-test ไปยังโครงสร้างการทดสอบ
copy_test_files() {
    echo "คัดลอกไฟล์ทดสอบไปยังโครงสร้างการทดสอบ..."
    
    cp -r /Users/witoonpongsilathong/MCP_folder/mm_dev_mode/project-test/test_files/* ${TEST_DIR}/ 2>/dev/null || :
    
    echo "✅ คัดลอกไฟล์ทดสอบเสร็จสิ้น"
}

# รันการทดสอบหน่วย
run_unit_tests() {
    echo -e "\n============================================"
    echo "รันการทดสอบหน่วย (Unit Tests)"
    echo "============================================"
    
    # รันการทดสอบหน่วยถ้ามีไฟล์ทดสอบ
    if [ -d "${TEST_DIR}/unit" ] && [ "$(ls -A ${TEST_DIR}/unit 2>/dev/null)" ]; then
        cd ${PROJECT_DIR} && python -m pytest ${TEST_DIR}/unit -v
    else
        echo "⚠️ ไม่พบไฟล์การทดสอบหน่วย"
    fi
}

# รันการทดสอบการทำงานร่วมกัน
run_integration_tests() {
    echo -e "\n============================================"
    echo "รันการทดสอบการทำงานร่วมกัน (Integration Tests)"
    echo "============================================"
    
    # รันการทดสอบการทำงานร่วมกันถ้ามีไฟล์ทดสอบ
    if [ -d "${TEST_DIR}/integration" ] && [ "$(ls -A ${TEST_DIR}/integration 2>/dev/null)" ]; then
        cd ${PROJECT_DIR} && python -m pytest ${TEST_DIR}/integration -v
    else
        echo "⚠️ ไม่พบไฟล์การทดสอบการทำงานร่วมกัน"
    fi
}

# รันการทดสอบระบบ
run_system_tests() {
    echo -e "\n============================================"
    echo "รันการทดสอบระบบ (System Tests)"
    echo "============================================"
    
    # ตรวจสอบว่าระบบกำลังทำงานอยู่
    echo "ตรวจสอบว่าระบบกำลังทำงานอยู่..."
    if curl -s http://localhost:8000/api/v1/health > /dev/null; then
        echo "✅ ระบบกำลังทำงานอยู่"
    else
        echo "⚠️ ระบบไม่ได้ทำงานอยู่ - กำลังเริ่มต้นระบบ..."
        cd ${PROJECT_DIR} && docker-compose up -d
        
        # รอให้ระบบเริ่มต้น
        echo "รอให้ระบบเริ่มต้น (30 วินาที)..."
        sleep 30
    fi
    
    # รันการทดสอบระบบถ้ามีไฟล์ทดสอบ
    if [ -d "${TEST_DIR}/system" ] && [ "$(ls -A ${TEST_DIR}/system 2>/dev/null)" ]; then
        cd ${PROJECT_DIR} && python -m pytest ${TEST_DIR}/system -v
    else
        echo "⚠️ ไม่พบไฟล์การทดสอบระบบ"
    fi
}

# รันการทดสอบประสิทธิภาพ
run_performance_tests() {
    echo -e "\n============================================"
    echo "รันการทดสอบประสิทธิภาพ (Performance Tests)"
    echo "============================================"
    
    # ตรวจสอบว่าระบบกำลังทำงานอยู่
    if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
        echo "⚠️ ระบบไม่ได้ทำงานอยู่ - กรุณาเริ่มต้นระบบก่อนรันการทดสอบประสิทธิภาพ"
        exit 1
    fi
    
    # รันการทดสอบประสิทธิภาพถ้ามีไฟล์ทดสอบ
    if [ -d "${TEST_DIR}/performance" ] && [ "$(ls -A ${TEST_DIR}/performance 2>/dev/null)" ]; then
        cd ${PROJECT_DIR} && python -m pytest ${TEST_DIR}/performance -v
    else
        echo "⚠️ ไม่พบไฟล์การทดสอบประสิทธิภาพ"
    fi
}

# รันการทดสอบการใช้งาน
run_usability_tests() {
    echo -e "\n============================================"
    echo "รันการทดสอบการใช้งาน (Usability Tests)"
    echo "============================================"
    
    # ตรวจสอบว่าระบบกำลังทำงานอยู่
    if ! curl -s http://localhost:8000/api/v1/health > /dev/null || ! curl -s http://localhost:8501 > /dev/null; then
        echo "⚠️ ระบบไม่ได้ทำงานอยู่ - กรุณาเริ่มต้นระบบก่อนรันการทดสอบการใช้งาน"
        exit 1
    fi
    
    # แสดงข้อมูลสำหรับการทดสอบการใช้งาน
    if [ -f "${TEST_DIR}/usability/frontend_test_script.md" ]; then
        echo "กรุณาปฏิบัติตามสคริปต์การทดสอบการใช้งานต่อไปนี้:"
        echo "====================================================="
        cat ${TEST_DIR}/usability/frontend_test_script.md
        echo "====================================================="
    else
        echo "⚠️ ไม่พบสคริปต์การทดสอบการใช้งาน"
    fi
    
    # รันสคริปต์ทดสอบความเร็วถ้ามี
    if [ -f "${TEST_DIR}/usability/load_time_test.sh" ]; then
        echo -e "\nกำลังรันการทดสอบความเร็วและการตอบสนอง..."
        bash ${TEST_DIR}/usability/load_time_test.sh
    fi
}

# แสดงเมนูทดสอบ
show_test_menu() {
    echo -e "\n============================================"
    echo "GraphRAG for PMQA 4.0 - เมนูทดสอบ"
    echo "============================================"
    echo "1) รันการทดสอบหน่วย (Unit Tests)"
    echo "2) รันการทดสอบการทำงานร่วมกัน (Integration Tests)"
    echo "3) รันการทดสอบระบบ (System Tests)"
    echo "4) รันการทดสอบประสิทธิภาพ (Performance Tests)"
    echo "5) รันการทดสอบการใช้งาน (Usability Tests)"
    echo "6) รันการทดสอบทั้งหมด"
    echo "7) เตรียมโครงสร้างการทดสอบ"
    echo "0) ออกจากโปรแกรม"
    echo "============================================"
    echo -n "เลือกตัวเลือก (0-7): "
    read choice
    
    case $choice in
        1) run_unit_tests ;;
        2) run_integration_tests ;;
        3) run_system_tests ;;
        4) run_performance_tests ;;
        5) run_usability_tests ;;
        6) 
            run_unit_tests
            run_integration_tests
            run_system_tests
            run_performance_tests
            run_usability_tests
            ;;
        7)
            prepare_test_directory
            copy_test_files
            ;;
        0) 
            echo "ออกจากโปรแกรม"
            exit 0
            ;;
        *)
            echo "ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่"
            ;;
    esac
    
    # แสดงเมนูอีกครั้งหลังจากดำเนินการเสร็จสิ้น
    show_test_menu
}

# Main execution
check_environment
show_test_menu