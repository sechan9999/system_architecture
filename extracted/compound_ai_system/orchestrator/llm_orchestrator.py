# orchestrator/llm_orchestrator.py
"""
LLM Orchestrator - Agent 결과를 종합하여 최종 판단 생성

실제 환경에서는 Claude API를 사용하지만, 데모에서는 Mock 로직 사용
"""
import json
from datetime import datetime
from typing import List
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schemas import Claim, AgentResult, FinalDecision, RiskLevel

class LLMOrchestrator:
    """LLM 기반 결과 종합 및 최종 판단"""
    
    def __init__(self, api_key: str = None, use_mock: bool = True):
        self.use_mock = use_mock
        if not use_mock and api_key:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-sonnet-4-20250514"
        else:
            self.client = None
    
    def _build_prompt(self, claim: Claim, agent_results: List[AgentResult]) -> str:
        """LLM 프롬프트 구성"""
        agent_summaries = []
        for result in agent_results:
            summary = f"""
### {result.agent_name}
- Risk Score: {result.risk_score:.2f}
- Confidence: {result.confidence:.2f}
- Findings:
{chr(10).join(f'  • {f}' for f in result.findings)}
- Evidence: {json.dumps(result.evidence, indent=2)}
"""
            agent_summaries.append(summary)
        
        prompt = f"""You are a healthcare fraud detection expert. Analyze the following claim and agent assessments.

## Claim Information
- Claim ID: {claim.claim_id}
- Provider ID: {claim.provider_id}
- Claim Amount: ${claim.claim_amount:,.2f}
- Procedure Code: {claim.procedure_code}
- Diagnosis Code: {claim.diagnosis_code}
- Provider Specialty: {claim.provider_specialty}
- Beneficiary Age: {claim.beneficiary_age}

## Agent Analysis Results
{''.join(agent_summaries)}

Provide fraud risk assessment in JSON format with:
overall_risk_score, risk_level, explanation, key_findings, recommended_action
"""
        return prompt
    
    def calculate_weighted_score(self, agent_results: List[AgentResult]) -> float:
        """가중 평균 점수 계산"""
        total_weight = sum(r.confidence for r in agent_results)
        if total_weight == 0:
            return 0.5
        
        weighted_sum = sum(
            r.risk_score * r.confidence 
            for r in agent_results
        )
        return weighted_sum / total_weight
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """점수 기반 리스크 레벨 결정"""
        if score < 0.3:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _determine_action(self, risk_level: RiskLevel) -> str:
        """리스크 레벨 기반 권장 액션"""
        action_map = {
            RiskLevel.LOW: "auto_approve",
            RiskLevel.MEDIUM: "manual_review",
            RiskLevel.HIGH: "flag_for_investigation",
            RiskLevel.CRITICAL: "auto_deny"
        }
        return action_map[risk_level]
    
    def _mock_synthesize(
        self, 
        claim: Claim, 
        agent_results: List[AgentResult]
    ) -> FinalDecision:
        """Mock 종합 판단 (API 없이 로직 기반)"""
        
        # 1. 가중 평균 점수 계산
        weighted_score = self.calculate_weighted_score(agent_results)
        
        # 2. 가장 심각한 findings 수집
        all_findings = []
        for result in agent_results:
            for finding in result.findings:
                if "이상" not in finding or "없음" not in finding:
                    all_findings.append(finding)
        
        # 중복 제거 및 상위 5개
        key_findings = list(set(all_findings))[:5]
        if not key_findings:
            key_findings = ["모든 분석에서 이상 징후 없음"]
        
        # 3. 리스크 레벨 및 액션 결정
        risk_level = self._determine_risk_level(weighted_score)
        action = self._determine_action(risk_level)
        
        # 4. 설명 생성
        high_risk_agents = [r for r in agent_results if r.risk_score > 0.5]
        if high_risk_agents:
            agent_names = ", ".join([a.agent_name.replace("Agent", "") for a in high_risk_agents])
            explanation = f"다수의 분석 시스템({agent_names})에서 위험 신호 감지. " \
                         f"가중 위험 점수 {weighted_score:.2f}로 {risk_level.value} 수준의 리스크 판정."
        else:
            explanation = f"모든 분석 시스템에서 정상 범위 내 결과. " \
                         f"가중 위험 점수 {weighted_score:.2f}로 승인 권장."
        
        return FinalDecision(
            claim_id=claim.claim_id,
            overall_risk_score=round(weighted_score, 3),
            risk_level=risk_level,
            explanation=explanation,
            key_findings=key_findings,
            recommended_action=action,
            agent_contributions=agent_results,
            processing_timestamp=datetime.now()
        )
    
    async def synthesize(
        self, 
        claim: Claim, 
        agent_results: List[AgentResult]
    ) -> FinalDecision:
        """Agent 결과를 종합하여 최종 판단 생성"""
        
        if self.use_mock or self.client is None:
            return self._mock_synthesize(claim, agent_results)
        
        # 실제 Claude API 호출 (API 키 있을 때)
        prompt = self._build_prompt(claim, agent_results)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        # JSON 파싱
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text
        
        result = json.loads(json_str.strip())
        
        return FinalDecision(
            claim_id=claim.claim_id,
            overall_risk_score=result["overall_risk_score"],
            risk_level=RiskLevel(result["risk_level"]),
            explanation=result["explanation"],
            key_findings=result["key_findings"],
            recommended_action=result["recommended_action"],
            agent_contributions=agent_results,
            processing_timestamp=datetime.now()
        )
