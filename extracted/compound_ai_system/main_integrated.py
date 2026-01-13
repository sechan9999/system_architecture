# main_integrated.py
"""
Compound AI Fraud Detection System - 통합 버전

모든 확장 기능이 통합된 전체 시스템:
1. Feature Store 연동
2. Knowledge Graph 통합
3. MLflow 모델 관리
4. FastAPI REST API

실행 방법:
    python main_integrated.py --mode demo    # 전체 데모 실행
    python main_integrated.py --mode api     # API 서버 실행
"""
import asyncio
import argparse
import sys
from datetime import datetime
from typing import List

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core imports
from models.schemas import Claim, FinalDecision, RiskLevel

# Agents
from agents.statistical_agent import StatisticalAnomalyAgent
from agents.ml_agent import MLPatternAgent
from agents.rule_agent import RuleComplianceAgent
from agents.feature_store_agent import FeatureStoreAgent
from agents.graph_agent import KnowledgeGraphAgent

# Orchestrator
from orchestrator.llm_orchestrator import LLMOrchestrator

# Extensions
from feature_store.feature_store_manager import FeatureStoreManager
from knowledge_graph.graph_manager import KnowledgeGraphManager


class IntegratedFraudDetectionSystem:
    """
    통합 Compound AI 사기 탐지 시스템
    
    5개의 전문화된 Agent와 LLM Orchestrator로 구성:
    1. StatisticalAnomalyAgent: 통계 기반 이상 탐지
    2. MLPatternAgent: ML 모델 기반 패턴 분석
    3. RuleComplianceAgent: 규칙 기반 컴플라이언스 검증
    4. FeatureStoreAgent: Feature Store 기반 실시간 분석
    5. KnowledgeGraphAgent: 네트워크 기반 관계 분석
    """
    
    def __init__(self, enable_all_agents: bool = True):
        print("=" * 60)
        print("🚀 INITIALIZING INTEGRATED FRAUD DETECTION SYSTEM")
        print("=" * 60)
        
        # Feature Store 초기화 및 데이터 생성
        print("\n📦 Setting up Feature Store...")
        self.feature_store_manager = FeatureStoreManager()
        self.feature_store_manager.generate_sample_data()
        
        # Agent 초기화
        print("\n🤖 Initializing Agents...")
        self.agents = [
            StatisticalAnomalyAgent(),
            MLPatternAgent(),
            RuleComplianceAgent(),
        ]
        
        if enable_all_agents:
            self.agents.extend([
                FeatureStoreAgent(),
                KnowledgeGraphAgent(),
            ])
        
        for agent in self.agents:
            print(f"   ✅ {agent.name} (weight: {agent.weight})")
        
        # Orchestrator 초기화
        print("\n🧠 Initializing LLM Orchestrator...")
        self.orchestrator = LLMOrchestrator(use_mock=True)
        
        print(f"\n✅ System ready with {len(self.agents)} agents")
    
    async def analyze_claim(self, claim: Claim, verbose: bool = True) -> FinalDecision:
        """단일 청구 분석"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔍 Analyzing Claim: {claim.claim_id}")
            print(f"   Provider: {claim.provider_id} | Amount: ${claim.claim_amount:,.2f}")
            print(f"{'='*60}")
        
        # 모든 Agent 병렬 실행
        agent_tasks = [agent.analyze(claim) for agent in self.agents]
        agent_results = await asyncio.gather(*agent_tasks)
        
        if verbose:
            for result in agent_results:
                emoji = "🔴" if result.risk_score > 0.6 else "🟡" if result.risk_score > 0.3 else "🟢"
                print(f"\n{emoji} {result.agent_name}:")
                print(f"   Risk: {result.risk_score:.2f} | Confidence: {result.confidence:.2f}")
                for f in result.findings[:2]:
                    print(f"   → {f}")
        
        # Orchestrator로 종합 판단
        final_decision = await self.orchestrator.synthesize(claim, agent_results)
        
        return final_decision
    
    async def batch_analyze(self, claims: List[Claim]) -> List[FinalDecision]:
        """배치 분석"""
        results = []
        for claim in claims:
            result = await self.analyze_claim(claim, verbose=False)
            results.append(result)
        return results


def print_final_decision(decision: FinalDecision):
    """최종 판단 출력"""
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
    
    print(f"\n{'='*60}")
    print(f"📋 FINAL DECISION: {decision.claim_id}")
    print(f"{'='*60}")
    print(f"Risk Level: {risk_emoji[decision.risk_level.value]} {decision.risk_level.value.upper()}")
    print(f"Risk Score: {decision.overall_risk_score:.3f}")
    print(f"Action: 👉 {decision.recommended_action.upper()}")
    print(f"\n📝 Explanation:")
    print(f"   {decision.explanation}")
    print(f"\n🔑 Key Findings:")
    for finding in decision.key_findings[:5]:
        print(f"   • {finding}")


async def run_demo():
    """전체 시스템 데모"""
    # 시스템 초기화
    system = IntegratedFraudDetectionSystem(enable_all_agents=True)
    
    # 테스트 케이스
    test_claims = [
        # Case 1: 정상 청구
        Claim(
            claim_id="DEMO001",
            provider_id="PRV010",
            beneficiary_id="BEN0010",
            procedure_code="99213",
            diagnosis_code="J06.9",
            claim_amount=120.0,
            service_date=datetime(2024, 11, 15),
            provider_specialty="General Practice",
            beneficiary_age=45,
            beneficiary_state="CA"
        ),
        # Case 2: 의심스러운 청구 (사기 링 Provider)
        Claim(
            claim_id="DEMO002",
            provider_id="PRV001",  # 사기 링 멤버
            beneficiary_id="BEN0020",
            procedure_code="93306",
            diagnosis_code="M54.5",
            claim_amount=8500.0,
            service_date=datetime(2024, 11, 16),
            provider_specialty="Cardiology",
            beneficiary_age=28,
            beneficiary_state="NY"
        ),
        # Case 3: 명백한 사기 (제재 Provider)
        Claim(
            claim_id="DEMO003",
            provider_id="PRV999",
            beneficiary_id="BEN0030",
            procedure_code="99215",
            diagnosis_code="Z00.00",
            claim_amount=950.0,
            service_date=datetime(2024, 11, 17),
            provider_specialty="General Practice",
            beneficiary_age=70,
            beneficiary_state="FL"
        ),
    ]
    
    print("\n" + "🏥 COMPOUND AI FRAUD DETECTION - INTEGRATED DEMO ".center(60, "="))
    
    # 각 청구 분석
    for claim in test_claims:
        try:
            decision = await system.analyze_claim(claim)
            print_final_decision(decision)
            print("\n" + "-" * 60)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # 요약 통계
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    print(f"   Total Claims Analyzed: {len(test_claims)}")
    print(f"   Agents Used: {len(system.agents)}")
    print("   Agent Contributions:")
    for agent in system.agents:
        print(f"      - {agent.name}")


def run_api_server():
    """API 서버 실행"""
    from api.server import run_server
    print("\n🚀 Starting FastAPI Server...")
    print("   Docs: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    run_server(host="0.0.0.0", port=8000)


def main():
    parser = argparse.ArgumentParser(description="Compound AI Fraud Detection System")
    parser.add_argument(
        "--mode", 
        choices=["demo", "api"], 
        default="demo",
        help="Execution mode: demo or api"
    )
    args = parser.parse_args()
    
    if args.mode == "demo":
        asyncio.run(run_demo())
    elif args.mode == "api":
        run_api_server()


if __name__ == "__main__":
    main()
