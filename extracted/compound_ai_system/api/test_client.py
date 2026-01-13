# api/test_client.py
"""
API 테스트 클라이언트

FastAPI 서버 테스트용 클라이언트입니다.
실제 환경에서는 curl이나 Postman으로 테스트할 수 있습니다.
"""
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')

from fastapi.testclient import TestClient
from api.server import app
from datetime import datetime
import json

# 테스트 클라이언트 생성
client = TestClient(app)

def test_health():
    """헬스 체크 테스트"""
    print("\n🔍 Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Version: {data['version']}")
    print(f"   Agents: {data['agents_count']}")
    return data

def test_agents():
    """Agent 목록 테스트"""
    print("\n🔍 Testing /agents endpoint...")
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    print(f"   Active Agents:")
    for agent in data:
        print(f"      - {agent['name']} (weight: {agent['weight']})")
    return data

def test_analyze_normal_claim():
    """정상 청구 분석 테스트"""
    print("\n🔍 Testing /analyze with normal claim...")
    
    payload = {
        "claim_id": "TEST001",
        "provider_id": "PRV003",
        "beneficiary_id": "BEN003",
        "procedure_code": "99213",
        "diagnosis_code": "J06.9",
        "claim_amount": 120.0,
        "service_date": "2024-11-15T00:00:00",
        "provider_specialty": "General Practice",
        "beneficiary_age": 45,
        "beneficiary_state": "CA"
    }
    
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    print(f"   Claim ID: {data['claim_id']}")
    print(f"   Risk Level: {data['risk_level'].upper()}")
    print(f"   Risk Score: {data['overall_risk_score']:.3f}")
    print(f"   Action: {data['recommended_action']}")
    print(f"   Processing Time: {data['processing_time_ms']:.2f}ms")
    return data

def test_analyze_suspicious_claim():
    """의심스러운 청구 분석 테스트"""
    print("\n🔍 Testing /analyze with suspicious claim...")
    
    payload = {
        "claim_id": "TEST002",
        "provider_id": "PRV002",
        "beneficiary_id": "BEN002",
        "procedure_code": "93306",
        "diagnosis_code": "M54.5",
        "claim_amount": 9500.0,
        "service_date": "2024-11-16T00:00:00",
        "provider_specialty": "Cardiology",
        "beneficiary_age": 28,
        "beneficiary_state": "NY"
    }
    
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    print(f"   Claim ID: {data['claim_id']}")
    print(f"   Risk Level: {data['risk_level'].upper()}")
    print(f"   Risk Score: {data['overall_risk_score']:.3f}")
    print(f"   Action: {data['recommended_action']}")
    print(f"   Key Findings:")
    for finding in data['key_findings'][:3]:
        print(f"      • {finding}")
    print(f"   Processing Time: {data['processing_time_ms']:.2f}ms")
    return data

def test_batch_analyze():
    """배치 분석 테스트"""
    print("\n🔍 Testing /batch-analyze endpoint...")
    
    payload = {
        "claims": [
            {
                "claim_id": "BATCH001",
                "provider_id": "PRV001",
                "beneficiary_id": "BEN001",
                "procedure_code": "99213",
                "diagnosis_code": "J06.9",
                "claim_amount": 150.0,
                "service_date": "2024-11-15T00:00:00",
                "provider_specialty": "General Practice",
                "beneficiary_age": 55,
                "beneficiary_state": "CA"
            },
            {
                "claim_id": "BATCH002",
                "provider_id": "PRV999",
                "beneficiary_id": "BEN002",
                "procedure_code": "99215",
                "diagnosis_code": "Z00.00",
                "claim_amount": 950.0,
                "service_date": "2024-11-16T00:00:00",
                "provider_specialty": "General Practice",
                "beneficiary_age": 70,
                "beneficiary_state": "FL"
            },
            {
                "claim_id": "BATCH003",
                "provider_id": "PRV003",
                "beneficiary_id": "BEN003",
                "procedure_code": "99214",
                "diagnosis_code": "E11.9",
                "claim_amount": 180.0,
                "service_date": "2024-11-17T00:00:00",
                "provider_specialty": "General Practice",
                "beneficiary_age": 62,
                "beneficiary_state": "TX"
            }
        ],
        "async_mode": False
    }
    
    response = client.post("/batch-analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    print(f"   Request ID: {data['request_id']}")
    print(f"   Total Claims: {data['total_claims']}")
    print(f"   Completed: {data['completed']}")
    print(f"\n   Summary:")
    print(f"      Risk Distribution: {data['summary']['risk_distribution']}")
    print(f"      Action Distribution: {data['summary']['action_distribution']}")
    print(f"      Avg Risk Score: {data['summary']['avg_risk_score']:.3f}")
    
    print(f"\n   Results:")
    for result in data['results']:
        emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
        print(f"      {result['claim_id']}: {emoji.get(result['risk_level'], '⚪')} {result['risk_level'].upper()} ({result['overall_risk_score']:.2f})")
    
    return data

def test_metrics():
    """메트릭 테스트"""
    print("\n🔍 Testing /metrics endpoint...")
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    print(f"   Total Requests: {data['total_requests']}")
    print(f"   Avg Processing Time: {data['avg_processing_time_ms']:.2f}ms")
    return data

def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("🧪 FASTAPI SERVER TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Agent List", test_agents),
        ("Normal Claim Analysis", test_analyze_normal_claim),
        ("Suspicious Claim Analysis", test_analyze_suspicious_claim),
        ("Batch Analysis", test_batch_analyze),
        ("Metrics", test_metrics),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            test_func()
            results[name] = "✅ PASSED"
        except Exception as e:
            results[name] = f"❌ FAILED: {e}"
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    for name, result in results.items():
        print(f"   {name}: {result}")
    
    return results


if __name__ == "__main__":
    run_all_tests()
