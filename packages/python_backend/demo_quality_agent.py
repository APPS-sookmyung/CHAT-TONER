# python_backend/demo_quality_agent.py

import asyncio
import logging
import json

from agents.quality_analysis_agent import OptimizedEnterpriseQualityAgent


# ---------- 1. RAG Service 목 ----------
class MockRAGService:
    """실제 RAG 대신, 미리 준비한 분석 JSON을 돌려주는 목 서비스"""

    async def ask_generative_question(self, query: str, context: str):
        # 실제로는 query를 보고 LLM + 벡터스토어를 쓰겠지만
        # 데모에서는 '이미 분석이 끝난 JSON'을 반환
        analysis_json = {
            "grammar_analysis": {
                "grammar_score": 68,
                "formality_score": 55,
                "readability_score": 72,
                "grammar_issues": [
                    {
                        "category": "존댓말/격식",
                        "original": "안녕하세요 고객님~",
                        "suggestion": "안녕하세요, 고객님.",
                        "reason": "기업 대외 커뮤니케이션에서는 이모티콘/물결 대신 깔끔한 존댓말 문장이 권장됩니다."
                    },
                    {
                        "category": "비격식 표현",
                        "original": "개쩌는 프로모션",
                        "suggestion": "매우 매력적인 프로모션",
                        "reason": "슬랭 대신 중립적인 비즈니스 표현 사용 필요"
                    },
                ],
            },
            "protocol_analysis": {
                "protocol_score": 60,
                "compliance_issues": [
                    {
                        "category": "브랜드 톤",
                        "original": "ㅎㅎ",
                        "suggestion": "문장을 마침표로 마무리",
                        "reason": "웃음 표현은 기업 공식 커뮤니케이션 가이드에 위배됨",
                        "severity": "low",
                    },
                    {
                        "category": "표현 규정",
                        "original": "개쩌는 프로모션",
                        "suggestion": "이번에 준비한 프로모션",
                        "reason": "비속어 및 과장 표현은 가이드라인상 사용 금지",
                        "severity": "high",
                    },
                ],
                "tone_assessment": {
                    "matches_company_tone": False,
                    "appropriateness": "too_casual",
                    "suggestions": [
                        "이모티콘, 물결, 비속어를 제거하고 문장을 정중하게 변경",
                    ],
                },
                "format_compliance": {
                    "meets_format": False,
                    "required_elements": [
                        "제목 또는 캠페인 명시",
                        "발신 조직/담당자 정보",
                    ],
                },
            },
            "overall_assessment": {
                "enterprise_readiness": 62,
                "primary_concerns": [
                    "전반적으로 캐주얼한 표현이 많음",
                    "브랜드 톤 가이드와 불일치",
                ],
                "strengths": [
                    "메시지의 핵심 의도는 명확함",
                ],
            },
        }

        print("\n[MockRAG] 벡터 스토어 + LLM 호출 시뮬레이션 (RAG 단계)")
        return {
            "success": True,
            "answer": json.dumps(analysis_json, ensure_ascii=False),
            "sources": [
                {
                    "title": "기업 이메일 커뮤니케이션 가이드",
                    "similarity": 0.92,
                },
                {
                    "title": "브랜드 톤 & 매뉴얼",
                    "similarity": 0.88,
                },
            ],
        }


# ---------- 2. DB Service 목 (Feedback 루프) ----------
class MockDBService:
    """분석 결과를 저장하는 부분을 프린트로 보여주기 위한 목 서비스"""

    async def get_company_profile(self, company_id: str):
        return {
            "id": company_id,
            "name": "데모 기업",
            "communication_style": "formal",
            "main_channels": ["email", "proposal"],
        }

    async def get_company_guidelines(self, company_id: str):
        return [
            {
                "document_name": "이메일 작성 가이드",
                "document_content": "외부 고객에게는 이모티콘, 비속어, 과도한 감탄사는 사용하지 않는다...",
            },
            {
                "document_name": "브랜드 톤 매뉴얼",
                "document_content": "친절하지만 과하지 않은 정중한 톤을 유지하며, 회사의 신뢰성을 훼손하는 표현은 금지한다...",
            },
        ]

    async def get_user_preferences(self, user_id: str, company_id: str):
        # 데모에선 간단히 빈 값
        return {}

    async def save_quality_analysis(self, analysis: dict):
        print("\n[MockDB] === Feedback 루프: 품질 분석 결과 저장 시뮬레이션 ===")
        summary = {
            "user_id": analysis.get("user_id"),
            "company_id": analysis.get("company_id"),
            "grammar_score": analysis.get("grammar_score"),
            "protocol_score": analysis.get("protocol_score"),
            "compliance_score": analysis.get("compliance_score"),
            "analysis_method": analysis.get("metadata", {}).get("analysis_method"),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))


# ---------- 3. 데모 실행 함수 ----------
async def main():
    # 로깅 설정: 에이전트 내부 로그가 콘솔에 보이도록
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    rag_service = MockRAGService()
    db_service = MockDBService()

    agent = OptimizedEnterpriseQualityAgent(
        rag_service=rag_service,
        db_service=db_service,
    )

    sample_text = "안녕하세요 고객님~ 이번에 저희가 준비한 쩌는 프로모션 안내드립니다 ㅋㅋㅋ"

    print("=== 입력 문장 ===")
    print(sample_text)

    result = await agent.analyze_enterprise_quality(
        text=sample_text,
        target_audience="외부 고객",
        context="이메일 초안",
        company_id="demo_company",
        user_id="demo_user",
    )

    print("\n=== 결과 요약 (Agent 출력) ===")
    print(
        f"Grammar / Formality / Readability  : "
        f"{result['grammar_score']} / {result['formality_score']} / {result['readability_score']}"
    )
    print(
        f"Protocol / Compliance               : "
        f"{result['protocol_score']} / {result['compliance_score']}"
    )
    print(f"사용된 RAG 문서 개수                : {result.get('rag_sources_count')}")

    print("\n--- 문장 개선 제안(일부) [Grammar] ---")
    for s in result["suggestions"]:
        print(f"- [{s['category']}] {s['original']}  →  {s['suggestion']}")
        print(f"  이유: {s['reason']}")

    print("\n--- 규정/브랜드 위반 제안(일부) [Protocol] ---")
    for s in result["protocol_suggestions"]:
        print(
            f"- ({s['severity']}) {s['original']}  →  {s['suggestion']}  "
            f"[{s['category']}]"
        )
        print(f"  이유: {s['reason']}")


if __name__ == "__main__":
    asyncio.run(main())
