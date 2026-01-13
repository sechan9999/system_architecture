# knowledge_graph/graph_manager.py
"""
Knowledge Graph Manager

Neo4j 기반 Knowledge Graph로 Provider-Beneficiary-Claim 관계를 분석합니다.

실제 환경:
- Neo4j 서버 연동
- Cypher 쿼리 실행
- 대규모 그래프 분석

데모 환경:
- NetworkX로 로컬 그래프 시뮬레이션
- 동일한 분석 로직 적용
"""
import networkx as nx
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import json

class KnowledgeGraphManager:
    """Knowledge Graph 관리 클래스"""
    
    def __init__(self, use_neo4j: bool = False, neo4j_uri: str = None):
        """
        Args:
            use_neo4j: True면 실제 Neo4j 서버 사용, False면 NetworkX 시뮬레이션
            neo4j_uri: Neo4j 연결 URI (예: "bolt://localhost:7687")
        """
        self.use_neo4j = use_neo4j
        
        if use_neo4j and neo4j_uri:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(neo4j_uri)
        else:
            # NetworkX로 로컬 그래프 생성
            self.graph = nx.DiGraph()
            self._initialize_sample_graph()
    
    def _initialize_sample_graph(self):
        """샘플 Knowledge Graph 생성"""
        np.random.seed(42)
        
        print("🔗 Initializing Knowledge Graph...")
        
        # Providers 생성 (100명)
        providers = [f"PRV{str(i).zfill(3)}" for i in range(1, 101)]
        for p in providers:
            specialty = np.random.choice([
                "General Practice", "Cardiology", "Orthopedics", 
                "Oncology", "Neurology", "Dermatology"
            ])
            self.graph.add_node(p, type="Provider", specialty=specialty)
        
        # Beneficiaries 생성 (500명)
        beneficiaries = [f"BEN{str(i).zfill(4)}" for i in range(1, 501)]
        for b in beneficiaries:
            age = np.random.randint(20, 85)
            self.graph.add_node(b, type="Beneficiary", age=age)
        
        # Claims 생성 및 관계 연결 (2000건)
        for i in range(1, 2001):
            claim_id = f"CLM{str(i).zfill(5)}"
            provider = np.random.choice(providers)
            beneficiary = np.random.choice(beneficiaries)
            amount = np.random.exponential(500)
            
            self.graph.add_node(claim_id, type="Claim", amount=amount)
            
            # Provider -> Claim (SUBMITTED)
            self.graph.add_edge(provider, claim_id, relationship="SUBMITTED")
            
            # Claim -> Beneficiary (FOR)
            self.graph.add_edge(claim_id, beneficiary, relationship="FOR")
        
        # 사기 네트워크 시뮬레이션: 일부 Provider들이 서로 환자를 주고받음
        fraud_ring = ["PRV001", "PRV002", "PRV003", "PRV004", "PRV005"]
        for i, p1 in enumerate(fraud_ring):
            for p2 in fraud_ring[i+1:]:
                # REFERS_TO 관계
                self.graph.add_edge(p1, p2, relationship="REFERS_TO", weight=np.random.randint(5, 20))
                self.graph.add_edge(p2, p1, relationship="REFERS_TO", weight=np.random.randint(5, 20))
        
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {self.graph.number_of_edges()}")
    
    # ============================================================
    # 그래프 분석 메서드
    # ============================================================
    
    def get_provider_network(self, provider_id: str) -> Dict:
        """
        Provider의 네트워크 분석
        
        Returns:
            - referral_partners: 상호 의뢰 관계에 있는 Provider 목록
            - shared_beneficiaries: 공유 환자 수
            - network_risk_score: 네트워크 기반 위험 점수
        """
        if provider_id not in self.graph:
            return {"error": "Provider not found"}
        
        result = {
            "provider_id": provider_id,
            "referral_partners": [],
            "shared_beneficiaries": 0,
            "network_risk_score": 0.0
        }
        
        # 의뢰 관계 파트너 찾기
        for neighbor in self.graph.neighbors(provider_id):
            edge_data = self.graph.get_edge_data(provider_id, neighbor)
            if edge_data and edge_data.get("relationship") == "REFERS_TO":
                result["referral_partners"].append({
                    "partner_id": neighbor,
                    "referral_count": edge_data.get("weight", 0)
                })
        
        # Provider가 제출한 Claim들
        provider_claims = [
            n for n in self.graph.neighbors(provider_id)
            if self.graph.nodes[n].get("type") == "Claim"
        ]
        
        # Claim들의 Beneficiary 수집
        provider_beneficiaries = set()
        for claim in provider_claims:
            for b in self.graph.neighbors(claim):
                if self.graph.nodes[b].get("type") == "Beneficiary":
                    provider_beneficiaries.add(b)
        
        result["total_beneficiaries"] = len(provider_beneficiaries)
        result["total_claims"] = len(provider_claims)
        
        # 네트워크 위험 점수 계산
        # - 많은 상호 의뢰 관계: 위험
        # - 높은 클러스터링: 위험
        referral_score = min(len(result["referral_partners"]) * 0.2, 1.0)
        
        # 클러스터링 계수 (높으면 위험)
        try:
            clustering = nx.clustering(self.graph.to_undirected(), provider_id)
        except:
            clustering = 0
        
        result["network_risk_score"] = round((referral_score + clustering) / 2, 3)
        
        return result
    
    def find_fraud_rings(self, min_size: int = 3) -> List[Dict]:
        """
        사기 링 탐지: 상호 환자 공유가 많은 Provider 그룹 찾기
        
        커뮤니티 탐지 알고리즘 사용
        """
        # Provider 노드만 추출
        provider_nodes = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "Provider"
        ]
        
        # Provider 간 서브그래프 생성 (REFERS_TO 관계만)
        provider_edges = []
        for u, v, d in self.graph.edges(data=True):
            if d.get("relationship") == "REFERS_TO":
                provider_edges.append((u, v, d.get("weight", 1)))
        
        if not provider_edges:
            return []
        
        # 서브그래프 생성
        subgraph = nx.Graph()
        subgraph.add_weighted_edges_from(provider_edges)
        
        # 연결 컴포넌트 찾기 (잠재적 사기 링)
        fraud_rings = []
        for component in nx.connected_components(subgraph):
            if len(component) >= min_size:
                members = list(component)
                
                # 링 내부 연결 강도 계산
                internal_edges = subgraph.subgraph(members).number_of_edges()
                max_edges = len(members) * (len(members) - 1) / 2
                density = internal_edges / max_edges if max_edges > 0 else 0
                
                fraud_rings.append({
                    "members": members,
                    "size": len(members),
                    "density": round(density, 3),
                    "risk_score": round(density * 0.8 + len(members) * 0.05, 3)
                })
        
        # 위험 점수로 정렬
        fraud_rings.sort(key=lambda x: x["risk_score"], reverse=True)
        return fraud_rings
    
    def get_beneficiary_journey(self, beneficiary_id: str) -> Dict:
        """
        Beneficiary의 의료 이용 여정 분석
        
        Doctor Shopping 탐지에 유용
        """
        if beneficiary_id not in self.graph:
            return {"error": "Beneficiary not found"}
        
        # Beneficiary와 연결된 Claim 찾기 (역방향)
        claims = []
        for predecessor in self.graph.predecessors(beneficiary_id):
            if self.graph.nodes[predecessor].get("type") == "Claim":
                claims.append(predecessor)
        
        # 각 Claim의 Provider 찾기
        providers = set()
        provider_visit_counts = defaultdict(int)
        
        for claim in claims:
            for predecessor in self.graph.predecessors(claim):
                if self.graph.nodes[predecessor].get("type") == "Provider":
                    providers.add(predecessor)
                    provider_visit_counts[predecessor] += 1
        
        # Doctor Shopping 점수: 많은 Provider 방문 = 높은 점수
        doctor_shopping_score = min(len(providers) / 10, 1.0)
        
        return {
            "beneficiary_id": beneficiary_id,
            "total_claims": len(claims),
            "unique_providers": len(providers),
            "provider_visits": dict(provider_visit_counts),
            "doctor_shopping_score": round(doctor_shopping_score, 3)
        }
    
    def get_claim_context(self, provider_id: str, beneficiary_id: str) -> Dict:
        """
        특정 Provider-Beneficiary 쌍에 대한 컨텍스트 정보
        """
        context = {
            "provider_id": provider_id,
            "beneficiary_id": beneficiary_id,
            "prior_claims_together": 0,
            "provider_network": None,
            "beneficiary_journey": None,
            "relationship_risk_score": 0.0
        }
        
        # Provider 네트워크 분석
        context["provider_network"] = self.get_provider_network(provider_id)
        
        # Beneficiary 여정 분석
        context["beneficiary_journey"] = self.get_beneficiary_journey(beneficiary_id)
        
        # 과거 청구 관계 확인
        if provider_id in self.graph and beneficiary_id in self.graph:
            provider_claims = [
                n for n in self.graph.neighbors(provider_id)
                if self.graph.nodes[n].get("type") == "Claim"
            ]
            
            for claim in provider_claims:
                if beneficiary_id in self.graph.neighbors(claim):
                    context["prior_claims_together"] += 1
        
        # 관계 위험 점수 계산
        provider_risk = context["provider_network"].get("network_risk_score", 0) if context["provider_network"] else 0
        beneficiary_risk = context["beneficiary_journey"].get("doctor_shopping_score", 0) if context["beneficiary_journey"] else 0
        
        context["relationship_risk_score"] = round((provider_risk + beneficiary_risk) / 2, 3)
        
        return context
    
    # ============================================================
    # Neo4j Cypher 쿼리 (실제 환경용)
    # ============================================================
    
    def execute_cypher(self, query: str, parameters: dict = None) -> List[Dict]:
        """
        Neo4j Cypher 쿼리 실행 (실제 Neo4j 서버 연동 시)
        """
        if not self.use_neo4j:
            raise ValueError("Neo4j is not enabled. Use NetworkX methods instead.")
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def close(self):
        """Neo4j 연결 종료"""
        if self.use_neo4j and hasattr(self, 'driver'):
            self.driver.close()


# ============================================================
# Cypher 쿼리 예시 (실제 Neo4j 환경용)
# ============================================================
CYPHER_QUERIES = {
    "provider_network": """
        MATCH (p:Provider {id: $provider_id})-[:REFERS_TO]->(partner:Provider)
        RETURN partner.id as partner_id, count(*) as referral_count
        ORDER BY referral_count DESC
        LIMIT 10
    """,
    
    "fraud_ring_detection": """
        MATCH (p1:Provider)-[:REFERS_TO]->(p2:Provider)-[:REFERS_TO]->(p3:Provider)
        WHERE p1 <> p3 AND (p1)-[:REFERS_TO]->(p3)
        RETURN p1.id, p2.id, p3.id, 
               count(*) as triangle_strength
        ORDER BY triangle_strength DESC
        LIMIT 20
    """,
    
    "doctor_shopping": """
        MATCH (b:Beneficiary {id: $beneficiary_id})<-[:FOR]-(c:Claim)<-[:SUBMITTED]-(p:Provider)
        WITH b, count(DISTINCT p) as unique_providers, collect(p.id) as providers
        WHERE unique_providers > 5
        RETURN b.id, unique_providers, providers
    """,
    
    "claim_context": """
        MATCH (p:Provider {id: $provider_id})-[:SUBMITTED]->(c:Claim)-[:FOR]->(b:Beneficiary {id: $beneficiary_id})
        OPTIONAL MATCH (p)-[:REFERS_TO]->(partner:Provider)
        WITH p, b, count(DISTINCT c) as prior_claims, collect(DISTINCT partner.id) as referral_partners
        RETURN p.id as provider, b.id as beneficiary, prior_claims, referral_partners
    """
}


# ============================================================
# 데모 실행
# ============================================================
def demo_knowledge_graph():
    """Knowledge Graph 데모"""
    print("=" * 60)
    print("🔗 KNOWLEDGE GRAPH DEMO")
    print("=" * 60)
    
    # 그래프 매니저 초기화
    manager = KnowledgeGraphManager(use_neo4j=False)
    
    # 1. Provider 네트워크 분석
    print("\n📊 Provider Network Analysis (PRV001):")
    network = manager.get_provider_network("PRV001")
    print(f"   Referral Partners: {len(network['referral_partners'])}")
    print(f"   Total Claims: {network['total_claims']}")
    print(f"   Network Risk Score: {network['network_risk_score']}")
    
    # 2. 사기 링 탐지
    print("\n🔍 Fraud Ring Detection:")
    fraud_rings = manager.find_fraud_rings(min_size=3)
    for i, ring in enumerate(fraud_rings[:3], 1):
        print(f"   Ring {i}: {ring['members']}")
        print(f"      Size: {ring['size']}, Density: {ring['density']}, Risk: {ring['risk_score']}")
    
    # 3. Beneficiary 여정 분석
    print("\n🚶 Beneficiary Journey Analysis (BEN0001):")
    journey = manager.get_beneficiary_journey("BEN0001")
    print(f"   Total Claims: {journey['total_claims']}")
    print(f"   Unique Providers: {journey['unique_providers']}")
    print(f"   Doctor Shopping Score: {journey['doctor_shopping_score']}")
    
    # 4. Claim Context
    print("\n📋 Claim Context (PRV001 -> BEN0001):")
    context = manager.get_claim_context("PRV001", "BEN0001")
    print(f"   Prior Claims Together: {context['prior_claims_together']}")
    print(f"   Relationship Risk Score: {context['relationship_risk_score']}")
    
    return manager


if __name__ == "__main__":
    demo_knowledge_graph()
