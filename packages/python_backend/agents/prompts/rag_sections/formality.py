def get_formality_section(
    business_style: str | None,
    negative_prompts: str | None,
    target: str,
    formality_criteria: dict
) -> str:

    # target별 격식도 기준 숫자 가져오기 (target.py에서 정의한 것)
    ideal_score = formality_criteria.get("ideal", 70)
    min_score = formality_criteria.get("min", 50)

    # 파일 로드 상태 처리
    style_text = f"""
### 비즈니스 문체 기준
{business_style}
""" if business_style else """
### 비즈니스 문체 기준
파일 미로드 — 한국 비즈니스 커뮤니케이션 일반 문체 원칙 적용
- 명확하고 간결한 표현
- 수동태보다 능동태
- 모호한 표현 지양 ("좀", "많이", "빨리")
"""

    negative_text = f"""
### 금지 표현/패턴
{negative_prompts}
""" if negative_prompts else """
### 금지 표현/패턴
파일 미로드 — 일반 금지 원칙 적용
- 과도한 감탄사 ("아", "진짜", "완전")
- 인터넷 줄임말
- 감정적 과장 표현
"""

    return f"""
## Formality 분석 기준
{style_text}
{negative_text}

## 이 수신자({target})의 격식도 기준
- 이상적인 격식도 점수: {ideal_score}점
- 최소 격식도 점수: {min_score}점
- {min_score}점 미만이면 severity high 이슈로 처리
- {ideal_score}점 기준으로 점수 산정

위 기준으로 분석하고,
justification에는 어떤 문체 기준과 수신자 특성을 근거로 했는지 명시하세요.
"""