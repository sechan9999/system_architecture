# main.py
"""
Compound AI Fraud Detection System - Main Entry Point
"""
import asyncio
from datetime import datetime
from typing import List
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')

from models.schemas import Claim, FinalDecision
from agents.statistical_agent import StatisticalAnomalyAgent
from agents.ml_agent import MLPatternAgent
from agents.rule_agent import RuleComplianceAgent
from orchestrator.llm_orchestrator import LLMOrchestrator

class FraudDetectionSystem:
    """Compound AI Fraud Detection System"""
    
    def __init__(self, anthropic_api_key: str = None, use_mock: bool = True):
        # Agent 초기화
        self.agents = [
            StatisticalAnomalyAgent(),
            MLPatternAgent(),
            RuleComplianceAgent(),
        ]
        
        # LLM Orchestrator 초기화
        self.orchestrator = LLMOrchestrator(
            api_key=anthropic_api_key, 
            use_mock=use_mock
        )
        
        print(f"✅ Fraud Detection System initialized with {len(self.agents)} agents")
        print(f"   Mode: {'Mock (Demo)' if use_mock else 'Live (Claude API)'}")
    
    async def analyze_claim(self, claim: Claim) -> FinalDecision:
        """단일 청구 분석"""
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing Claim: {claim.claim_id}")
        print(f"   Provider: {claim.provider_id} | Amount: ${claim.claim_amount:,.2f}")
        print(f"{'='*60}")
        
        # Step 1: 모든 Agent 병렬 실행
        agent_tasks = [
            agent.analyze(claim) 
            for agent in self.agents
        ]
        agent_results = await asyncio.gather(*agent_tasks)
        
        # Agent 결과 출력
        for result in agent_results:
            emoji = "🔴" if result.risk_score > 0.6 else "🟡" if result.risk_score > 0.3 else "🟢"
            print(f"\n{emoji} {result.agent_name}:")
            print(f"   Risk Score: {result.risk_score:.2f} | Confidence: {result.confidence:.2f}")
            for finding in result.findings:
                print(f"   → {finding}")
        
        # Step 2: 가중 평균 점수
        weighted_score = self.orchestrator.calculate_weighted_score(agent_results)
        print(f"\n📈 Weighted Average Score: {weighted_score:.3f}")
        
        # Step 3: LLM Orchestrator로 최종 판단
        print(f"\n🤖 Orchestrator synthesizing results...")
        final_decision = await self.orchestrator.synthesize(claim, agent_results)
        
        return final_decision
    
    async def batch_analyze(self, claims: List[Claim]) -> List[FinalDecision]:
        """배치 청구 분석"""
        results = []
        for claim in claims:
            result = await self.analyze_claim(claim)
            results.append(result)
        return results


def print_decision(decision: FinalDecision):
    """최종 판단 결과 출력"""
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡", 
        "high": "🟠",
        "critical": "🔴"
    }
    
    print(f"\n{'='*60}")
    print(f"📋 FINAL DECISION: {decision.claim_id}")
    print(f"{'='*60}")
    print(f"Risk Level: {risk_emoji[decision.risk_level.value]} {decision.risk_level.value.upper()}")
    print(f"Risk Score: {decision.overall_risk_score:.3f}")
    print(f"Action: 👉 {decision.recommended_action.upper()}")
    print(f"\n📝 Explanation:")
    print(f"   {decision.explanation}")
    print(f"\n🔑 Key Findings:")
    for finding in decision.key_findings:
        print(f"   • {finding}")


async def main():
    """메인 실행 함수"""
    # 시스템 초기화 (Mock 모드)
    system = FraudDetectionSystem(use_mock=True)
    
    # 테스트 청구 데이터
    test_claims = [
        # Case 1: 정상 청구
        Claim(
            claim_id="CLM001",
            provider_id="PRV001",
            beneficiary_id="BEN001",
            procedure_code="99213",
            diagnosis_code="J06.9",
            claim_amount=120.0,
            service_date=datetime(2024, 11, 15),
            provider_specialty="General Practice",
            beneficiary_age=45,
            beneficiary_state="CA"
        ),
        # Case 2: 의심스러운 청구
        Claim(
            claim_id="CLM002",
            provider_id="PRV002",
            beneficiary_id="BEN002",
            procedure_code="93306",
            diagnosis_code="M54.5",
            claim_amount=9500.0,
            service_date=datetime(2024, 11, 16),
            provider_specialty="Cardiology",
            beneficiary_age=28,
            beneficiary_state="NY"
        ),
        # Case 3: 명백한 사기
        Claim(
            claim_id="CLM003",
            provider_id="PRV999",
            beneficiary_id="BEN003",
            procedure_code="99215",
            diagnosis_code="Z00.00",
            claim_amount=950.0,
            service_date=datetime(2025, 12, 25),
            provider_specialty="General Practice",
            beneficiary_age=70,
            beneficiary_state="FL"
        ),
    ]
    
    print("\n" + "🏥 COMPOUND AI FRAUD DETECTION SYSTEM ".center(60, "="))
    print("=" * 60)
    
    # 분석 실행
    for claim in test_claims:
        try:
            decision = await system.analyze_claim(claim)
            print_decision(decision)
            print("\n" + "-" * 60)
        except Exception as e:
            print(f"❌ Error processing claim {claim.claim_id}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
