def get_protocol_section(
    rag_chunks: list[str] | None,
    company_name: str | None,
    target: str,
    context: str
) -> str:

    # RAG 완전 실패
    if not rag_chunks:
        return f"""
## Protocol 분석 기준
{'회사 가이드라인(' + company_name + ')을 불러오지 못했습니다.' if company_name else '회사 가이드라인을 불러오지 못했습니다.'}
한국 비즈니스 커뮤니케이션 일반 프로토콜을 기준으로 분석하세요.

### Fallback 기준
**공통**
- 수신자에게 적절한 호칭 사용
- 민감한 내부 정보 외부 노출 금지
- 개인 감정/갈등의 공식 문서 포함 금지

**수신자({target}) 관련**
- 외부 수신자(클라이언트/협력업체): 내부 채널명, 내부 인원 정보 노출 금지
- 상위 직급(직속상사): 두괄식 보고 원칙
- 동료/후배: 명확한 action item 포함 권장

**문서 유형({context}) 관련**
- 이메일: 제목-본문-서명 구조 준수
- 메시지: 단일 요점, 간결성 우선
- 보고서: 사실/데이터 기반, 주관 배제
- 회의록: 결정사항과 Action Item 명확히 구분
- 공지사항: 대상/기한/문의처 명시

justification에는 "일반 비즈니스 프로토콜 기준 (회사 가이드라인 미로드)" 으로 명시하세요.
"""

    # RAG 청크 있음 — 멀티 테넌트 고려해서 company_name 명시
    chunks_text = "\n\n---\n\n".join(rag_chunks)

    company_label = f"({company_name})" if company_name else ""

    return f"""
## Protocol 분석 기준 — 회사 가이드라인 {company_label}

### 검색된 가이드라인
{chunks_text}

### 분석 지시
- 위 가이드라인을 **최우선 기준**으로 삼으세요
- 수신자({target})와 문서 유형({context})에 관련된 조항을 중심으로 판단하세요
- 가이드라인에 명시되지 않은 항목은 한국 비즈니스 일반 관행으로 보완하세요

### justification 작성 방법
- 가이드라인 기준: 근거가 된 조항/섹션 내용을 요약해서 명시
  예) "3장 이메일 작성 원칙 중 '외부 발송 시 내부 채널 정보 노출 금지' 조항 기준"
- 일반 관행 보완: "가이드라인 미포함 항목 — 일반 관행 적용" 으로 명시
"""