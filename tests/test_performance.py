import pytest
import time
import asyncio
import statistics
import json
import requests
from concurrent.futures import ThreadPoolExecutor

# Define test API endpoints (adjust as needed for the actual environment)
BASE_URL = "http://localhost:8000/api/v1"
ENDPOINTS = {
    "health": f"{BASE_URL}/health",
    "vector_search": f"{BASE_URL}/search/vector",
    "graph_search": f"{BASE_URL}/search/graph",
    "hybrid_search": f"{BASE_URL}/search/hybrid",
    "claude_ask": f"{BASE_URL}/claude/ask"
}

# Test configurations
NUM_REQUESTS = 20  # Number of requests per test
CONCURRENT_USERS = 5  # Number of concurrent users/requests
SEARCH_QUERIES = [
    "การวางแผนยุทธศาสตร์",
    "การบริหารจัดการองค์กร",
    "การพัฒนาบุคลากร",
    "การประเมินผลการปฏิบัติงาน",
    "การนำองค์การ"
]

# Performance metrics thresholds
RESPONSE_TIME_THRESHOLDS = {
    "health": 0.5,  # 500ms
    "vector_search": 2.0,  # 2s
    "graph_search": 2.0,  # 2s
    "hybrid_search": 3.0,  # 3s
    "claude_ask": 10.0  # 10s
}

# Helper functions
def make_request(url, method="GET", json_data=None):
    """ส่งคำขอไปยัง API และวัดเวลาการตอบสนอง"""
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            "status_code": response.status_code,
            "response_time": elapsed_time,
            "success": 200 <= response.status_code < 300
        }
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            "status_code": 0,
            "response_time": elapsed_time,
            "success": False,
            "error": str(e)
        }

def run_concurrent_requests(url, method="GET", json_data=None, num_requests=NUM_REQUESTS, concurrent_users=CONCURRENT_USERS):
    """รันคำขอพร้อมกันหลายคำขอ"""
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        if method == "GET":
            futures = [executor.submit(make_request, url, method) for _ in range(num_requests)]
        else:
            # สำหรับคำขอ POST ที่มีข้อมูล JSON
            futures = [executor.submit(make_request, url, method, json_data) for _ in range(num_requests)]
        
        results = [future.result() for future in futures]
    
    return results

def analyze_results(results, endpoint_name):
    """วิเคราะห์ผลลัพธ์และสร้างรายงาน"""
    response_times = [result["response_time"] for result in results if result["success"]]
    success_count = sum(1 for result in results if result["success"])
    error_count = len(results) - success_count
    
    if not response_times:
        return {
            "endpoint": endpoint_name,
            "success_rate": 0,
            "error_count": error_count,
            "avg_time": None,
            "min_time": None,
            "max_time": None,
            "p90_time": None,
            "p95_time": None,
            "p99_time": None,
            "requests_per_second": 0,
            "threshold": RESPONSE_TIME_THRESHOLDS.get(endpoint_name, 0),
            "passed": False
        }
    
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    
    # คำนวณเปอร์เซ็นไทล์
    sorted_times = sorted(response_times)
    p90_index = int(0.9 * len(sorted_times))
    p95_index = int(0.95 * len(sorted_times))
    p99_index = int(0.99 * len(sorted_times))
    
    p90_time = sorted_times[p90_index] if len(sorted_times) > p90_index else sorted_times[-1]
    p95_time = sorted_times[p95_index] if len(sorted_times) > p95_index else sorted_times[-1]
    p99_time = sorted_times[p99_index] if len(sorted_times) > p99_index else sorted_times[-1]
    
    # คำนวณ requests per second
    total_time = sum(response_times)
    requests_per_second = len(response_times) / total_time if total_time > 0 else 0
    
    # ตรวจสอบว่าผ่านเกณฑ์หรือไม่
    threshold = RESPONSE_TIME_THRESHOLDS.get(endpoint_name, float("inf"))
    passed = avg_time < threshold
    
    return {
        "endpoint": endpoint_name,
        "success_rate": success_count / len(results) if results else 0,
        "error_count": error_count,
        "avg_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "p90_time": p90_time,
        "p95_time": p95_time,
        "p99_time": p99_time,
        "requests_per_second": requests_per_second,
        "threshold": threshold,
        "passed": passed
    }

# การทดสอบประสิทธิภาพ
@pytest.mark.performance
class TestPerformance:
    
    @pytest.fixture(scope="class")
    def check_api_availability(self):
        """ตรวจสอบว่า API พร้อมใช้งานหรือไม่"""
        try:
            response = requests.get(ENDPOINTS["health"], timeout=5)
            if response.status_code != 200:
                pytest.skip("API is not available or not healthy")
        except Exception:
            pytest.skip("API is not available")
    
    def test_health_endpoint_performance(self, check_api_availability):
        """ทดสอบประสิทธิภาพของ health endpoint"""
        print(f"\nทดสอบประสิทธิภาพของ health endpoint...")
        results = run_concurrent_requests(ENDPOINTS["health"])
        analysis = analyze_results(results, "health")
        
        print_performance_report(analysis)
        
        # ตรวจสอบว่าผ่านเกณฑ์
        assert analysis["success_rate"] > 0.95, "อัตราความสำเร็จต่ำกว่า 95%"
        assert analysis["avg_time"] < RESPONSE_TIME_THRESHOLDS["health"], f"เวลาเฉลี่ยเกินกว่า {RESPONSE_TIME_THRESHOLDS['health']} วินาที"
    
    def test_vector_search_performance(self, check_api_availability):
        """ทดสอบประสิทธิภาพของ vector search endpoint"""
        print(f"\nทดสอบประสิทธิภาพของ vector search endpoint...")
        
        all_results = []
        for query in SEARCH_QUERIES:
            json_data = {"query": query, "limit": 5}
            results = run_concurrent_requests(
                ENDPOINTS["vector_search"],
                method="POST",
                json_data=json_data
            )
            all_results.extend(results)
        
        analysis = analyze_results(all_results, "vector_search")
        print_performance_report(analysis)
        
        # ตรวจสอบว่าผ่านเกณฑ์
        assert analysis["success_rate"] > 0.95, "อัตราความสำเร็จต่ำกว่า 95%"
        assert analysis["avg_time"] < RESPONSE_TIME_THRESHOLDS["vector_search"], f"เวลาเฉลี่ยเกินกว่า {RESPONSE_TIME_THRESHOLDS['vector_search']} วินาที"
    
    def test_graph_search_performance(self, check_api_availability):
        """ทดสอบประสิทธิภาพของ graph search endpoint"""
        print(f"\nทดสอบประสิทธิภาพของ graph search endpoint...")
        
        all_results = []
        for query in SEARCH_QUERIES:
            json_data = {"query": query, "limit": 5}
            results = run_concurrent_requests(
                ENDPOINTS["graph_search"],
                method="POST",
                json_data=json_data
            )
            all_results.extend(results)
        
        analysis = analyze_results(all_results, "graph_search")
        print_performance_report(analysis)
        
        # ตรวจสอบว่าผ่านเกณฑ์
        assert analysis["success_rate"] > 0.95, "อัตราความสำเร็จต่ำกว่า 95%"
        assert analysis["avg_time"] < RESPONSE_TIME_THRESHOLDS["graph_search"], f"เวลาเฉลี่ยเกินกว่า {RESPONSE_TIME_THRESHOLDS['graph_search']} วินาที"
    
    def test_hybrid_search_performance(self, check_api_availability):
        """ทดสอบประสิทธิภาพของ hybrid search endpoint"""
        print(f"\nทดสอบประสิทธิภาพของ hybrid search endpoint...")
        
        all_results = []
        for query in SEARCH_QUERIES:
            json_data = {"query": query, "limit": 5}
            results = run_concurrent_requests(
                ENDPOINTS["hybrid_search"],
                method="POST",
                json_data=json_data
            )
            all_results.extend(results)
        
        analysis = analyze_results(all_results, "hybrid_search")
        print_performance_report(analysis)
        
        # ตรวจสอบว่าผ่านเกณฑ์
        assert analysis["success_rate"] > 0.95, "อัตราความสำเร็จต่ำกว่า 95%"
        assert analysis["avg_time"] < RESPONSE_TIME_THRESHOLDS["hybrid_search"], f"เวลาเฉลี่ยเกินกว่า {RESPONSE_TIME_THRESHOLDS['hybrid_search']} วินาที"
    
    def test_claude_ask_performance(self, check_api_availability):
        """ทดสอบประสิทธิภาพของ Claude ask endpoint"""
        print(f"\nทดสอบประสิทธิภาพของ Claude ask endpoint...")
        
        all_results = []
        for query in SEARCH_QUERIES[:2]:  # ใช้แค่ 2 คำถามเนื่องจาก API นี้อาจใช้เวลานาน
            json_data = {"question": f"อธิบายเกี่ยวกับ {query} ในบริบทของ PMQA 4.0"}
            results = run_concurrent_requests(
                ENDPOINTS["claude_ask"],
                method="POST",
                json_data=json_data,
                num_requests=5,  # ลดจำนวนคำขอลงเพื่อประหยัดเวลา
                concurrent_users=2  # ลดจำนวนผู้ใช้พร้อมกันลงเพื่อไม่ให้เกิดการโอเวอร์โหลด
            )
            all_results.extend(results)
        
        analysis = analyze_results(all_results, "claude_ask")
        print_performance_report(analysis)
        
        # ตรวจสอบว่าผ่านเกณฑ์ (สำหรับ endpoint นี้ อาจยอมรับอัตราความสำเร็จที่ต่ำกว่าได้)
        assert analysis["success_rate"] > 0.8, "อัตราความสำเร็จต่ำกว่า 80%"
        assert analysis["avg_time"] < RESPONSE_TIME_THRESHOLDS["claude_ask"], f"เวลาเฉลี่ยเกินกว่า {RESPONSE_TIME_THRESHOLDS['claude_ask']} วินาที"

def print_performance_report(analysis):
    """พิมพ์รายงานประสิทธิภาพในรูปแบบที่อ่านง่าย"""
    print(f"รายงานประสิทธิภาพสำหรับ {analysis['endpoint']}:")
    print(f"- อัตราความสำเร็จ: {analysis['success_rate'] * 100:.2f}%")
    print(f"- จำนวนข้อผิดพลาด: {analysis['error_count']}")
    
    if analysis['avg_time'] is not None:
        print(f"- เวลาเฉลี่ย: {analysis['avg_time']:.4f}s")
        print(f"- เวลาต่ำสุด: {analysis['min_time']:.4f}s")
        print(f"- เวลาสูงสุด: {analysis['max_time']:.4f}s")
        print(f"- เวลา P90: {analysis['p90_time']:.4f}s")
        print(f"- เวลา P95: {analysis['p95_time']:.4f}s")
        print(f"- เวลา P99: {analysis['p99_time']:.4f}s")
        print(f"- คำขอต่อวินาที: {analysis['requests_per_second']:.2f}")
    
    threshold_status = "✓ ผ่าน" if analysis['passed'] else "✗ ไม่ผ่าน"
    print(f"- เกณฑ์: {analysis['threshold']:.4f}s - {threshold_status}")

# สามารถรันการทดสอบนี้แบบ standalone ได้ (ไม่ผ่าน pytest)
if __name__ == "__main__":
    # ตรวจสอบว่า API พร้อมใช้งานหรือไม่
    try:
        response = requests.get(ENDPOINTS["health"], timeout=5)
        if response.status_code != 200:
            print("API is not available or not healthy")
            exit(1)
    except Exception as e:
        print(f"API is not available: {str(e)}")
        exit(1)
    
    # ทดสอบทุก endpoint
    print("เริ่มการทดสอบประสิทธิภาพ...")
    
    # ทดสอบ health endpoint
    results = run_concurrent_requests(ENDPOINTS["health"])
    analysis = analyze_results(results, "health")
    print_performance_report(analysis)
    
    # ทดสอบ search endpoints
    for endpoint_name in ["vector_search", "graph_search", "hybrid_search"]:
        all_results = []
        for query in SEARCH_QUERIES:
            json_data = {"query": query, "limit": 5}
            results = run_concurrent_requests(
                ENDPOINTS[endpoint_name],
                method="POST",
                json_data=json_data
            )
            all_results.extend(results)
        
        analysis = analyze_results(all_results, endpoint_name)
        print_performance_report(analysis)
    
    # ทดสอบ Claude ask endpoint
    all_results = []
    for query in SEARCH_QUERIES[:2]:
        json_data = {"question": f"อธิบายเกี่ยวกับ {query} ในบริบทของ PMQA 4.0"}
        results = run_concurrent_requests(
            ENDPOINTS["claude_ask"],
            method="POST",
            json_data=json_data,
            num_requests=5,
            concurrent_users=2
        )
        all_results.extend(results)
    
    analysis = analyze_results(all_results, "claude_ask")
    print_performance_report(analysis)
    
    print("การทดสอบประสิทธิภาพเสร็จสิ้น")