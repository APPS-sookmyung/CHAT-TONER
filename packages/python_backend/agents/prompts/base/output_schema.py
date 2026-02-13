OUTPUT_SCHEMA = """
다음 JSON 형식으로만 출력하세요. 다른 텍스트 없음.

{
  "grammar": {
    "score": 0-100,
    "justification": "점수 근거 (가능하면 출처 명시, 없으면 적용 원칙 설명)",
    "issues": [
      {
        "severity": "high|medium|low",
        "location": "원문에서 문제 구절 (정확히 복사)",
        "description": "문제 설명",
        "suggestion": "수정 제안"
      }
    ]
  },
  "formality": {
    "score": 0-100,
    "justification": "점수 근거 (가능하면 출처 명시, 없으면 적용 원칙 설명)",
    "issues": [
      {
        "severity": "high|medium|low",
        "location": "원문에서 문제 구절 (정확히 복사)",
        "description": "문제 설명",
        "suggestion": "수정 제안"
      }
    ]
  },
  "protocol": {
    "score": 0-100,
    "justification": "점수 근거 (가능하면 출처 명시, 없으면 일반 비즈니스 관행 기준으로 명시)",
    "issues": [
      {
        "severity": "high|medium|low",
        "location": "원문에서 문제 구절 (정확히 복사)",
        "description": "문제 설명",
        "suggestion": "수정 제안"
      }
    ]
  },
  "final_text": "grammar + formality + protocol 세 기준을 동시에 반영한 최종 변환 텍스트",
  "final_text_warning": null | "high_severity_issues_remain",
  "summary": "전체 평가 한 줄 요약"
}

## 제약
- 각 섹션 이슈 최대 5개, severity high 우선
- final_text는 원문 의미 유지하면서 최소한으로 수정
- JSON만 출력, 마크다운 코드블록 없음
"""