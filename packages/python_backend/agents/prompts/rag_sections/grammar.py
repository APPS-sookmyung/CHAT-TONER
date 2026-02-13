def get_grammar_section(
    grammar_rules: str | None,
    readability_rules: str | None
) -> str:

    # 둘 다 로드 실패
    if not grammar_rules and not readability_rules:
        return """
## Grammar 분석 기준
가이드라인 파일을 불러오지 못했습니다.
아래 한국어 비즈니스 문서 일반 원칙을 기준으로 분석하세요.

### Fallback 기준
**맞춤법/문법**
- 한글 맞춤법 표준 준수
- 조사 오용 없을 것 (을/를, 이/가, 은/는 구분)
- 문장 종결 일관성 ("-습니다" 혼용 금지)

**띄어쓰기**
- 단어 단위 띄어쓰기 준수
- 의존명사 띄어쓰기 ("것", "수", "바" 등)

**가독성**
- 한 문장 50자 이내 권장
- 한 문장에 하나의 의미만
- 중복 표현 제거

justification에는 "한국어 맞춤법 일반 원칙 기준 (가이드라인 미로드)" 으로 명시하세요.
"""

    # 부분 로드
    grammar_text = f"""
### 문법 규칙
{grammar_rules}
""" if grammar_rules else """
### 문법 규칙
파일 미로드 — 한국어 맞춤법 표준 원칙 적용
"""

    readability_text = f"""
### 가독성 규칙
{readability_rules}
""" if readability_rules else """
### 가독성 규칙
파일 미로드 — 문장 50자 이내, 한 문장 한 의미 원칙 적용
"""

    return f"""
## Grammar 분석 기준
{grammar_text}
{readability_text}

위 규칙을 기준으로 분석하고,
justification에는 어떤 규칙을 근거로 했는지 명시하세요.
로드된 파일 기준이면 해당 규칙명을,
fallback 기준이면 "일반 원칙 적용" 으로 명시하세요.
"""