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
    ],
    "markdown_explanation": "PromptEngineer 스타일 마크다운 설명 (### 입력 분석, ### 개선 포인트, ### 요약)"
  },
  "formality": {
    "score": 0-100,
    "justification": "점수 근거",
    "issues": [...],
    "markdown_explanation": "### 귀사 가이드라인 안내 (있을 경우), ### 격식도 분석, ### 이렇게 고치셔야 하는 이유"
  },
  "protocol": {
    "score": 0-100,
    "justification": "점수 근거",
    "issues": [...],
    "markdown_explanation": "### 귀사 가이드라인 안내 (있을 경우), ### 프로토콜 분석, ### 이렇게 고치셔야 하는 이유"
  },
  "final_text": "grammar + formality + protocol 세 기준을 동시에 반영한 최종 변환 텍스트",
  "final_text_warning": null | "high_severity_issues_remain",
  "summary": "전체 평가 한 줄 요약"
}

## markdown_explanation 형식 지침

각 섹션의 markdown_explanation은 사용자에게 **왜 고쳐야 하는지 친절하게 코칭**하는 어조로 작성하세요.

### Grammar markdown_explanation 형식:
```markdown
### 입력 분석

| 항목 | 분석 |
|------|------|
| 현재 말투 | (캐주얼/반말/존댓말 등) |
| 톤/어조 | (공격적/친근/무관심 등) |
| 격식 수준 | N/10 |

### 개선 포인트
- **[포인트 1]**: "현재 표현"은 ~한 인상을 줄 수 있으므로, ~하시는 것이 좋습니다.
- **[포인트 2]**: ...

### 요약
> 사용자의 입력은 "..."인데, 문법적으로 ~한 부분을 개선하시면 더욱 명확한 의사소통이 가능합니다.
```

### Formality markdown_explanation 형식:
```markdown
### 귀사 가이드라인 안내
(기업 가이드라인이 있는 경우에만)
- "귀사의 [문서 제목]([문서 N])에 따르면, ~해야 합니다."

### 격식도 분석

| 항목 | 현재 수준 | 목표 수준 | 조정 내용 |
|------|-----------|-----------|-----------|
| 높임법 | ... | ... | ... |
| 종결어미 | ... | ... | ... |

### 이렇게 고치셔야 하는 이유
- ~하시면 ~로 오해받을 수 있으므로...
```

### Protocol markdown_explanation 형식:
```markdown
### 귀사 가이드라인 안내
(기업 가이드라인이 있는 경우에만)
- "귀사의 [문서 제목]([문서 N])에 따르면, ~해야 합니다."

### 프로토콜 분석

| 위반 항목 | 현재 표현 | 위반 프로토콜 | 수정 제안 |
|-----------|-----------|---------------|-----------|
| ... | ... | ... | ... |

### 이렇게 고치셔야 하는 이유
- ~하시면 ~로 비춰질 수 있으므로...
```

## 제약
- 각 섹션 이슈 최대 5개, severity high 우선
- final_text는 원문 의미 유지하면서 최소한으로 수정
- markdown_explanation은 친절한 코칭 어조 (~하시는 것이 좋습니다)
- JSON만 출력, 마크다운 코드블록 없음
"""