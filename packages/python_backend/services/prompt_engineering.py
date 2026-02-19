"""
프롬프트 엔지니어링 서비스
컨텍스트별, 사용자별 맞춤 프롬프트 생성
- 상황별 네거티브 프롬프트
- 스타일별 템플릿
- 사용자 성향 기반 제약사항 문장 생성
- 사용자 프로필 + 상황 기반 전체 프롬프트 생성

컨텍스트(업무, 보고서, 개인적 글)에 따라 부정 프롬프트, 문체 가이드, 사용자 특성 정보
까지 포함된 프롬프트를 최종 생성해줌

"""

from typing import Dict, List, Any, Optional
import os
import json

class PromptEngineer:
    """프롬프트 생성 및 관리 클래스"""
    
    def __init__(self):
        self.base_negative_prompts = self._init_base_negative_prompts()
        self.context_specific_prompts = self._init_context_prompts()
    
    def _init_base_negative_prompts(self) -> Dict[str, str]:
        """기본 네거티브 프롬프트 초기화"""
        return {
            "common": """다음 사항들을 피해주세요:
- 과도한 미사여구나 꾸밈말 사용
- 같은 의미의 단어나 구문 반복
- 불필요한 쉼표 남발
- 형식적인 틀에만 치중하여 내용이 빈약해지는 것
- 과도한 불렛 포인트나 리스트 형태 사용
- 이모티콘이나 특수문자 남용
- ChatGPT스럽거나 AI가 작성한 듯한 인위적인 표현
- 지나치게 정형화된 문체나 구조""",
            
            "business": """업무용 텍스트에서 다음을 피해주세요:
- 과도한 존댓말이나 겸손 표현
- 불필요한 서론이나 인사말 반복
- 지나치게 딱딱하거나 기계적인 표현
- 본질과 관련 없는 형식적 문구""",
            
            "personal": """개인적 소통에서 다음을 피해주세요:
- 지나치게 격식차린 표현
- 감정 없는 건조한 톤
- 불필요한 설명이나 부연
- 일방적이거나 차가운 느낌의 문체"""
        }
    
    def _init_context_prompts(self) -> Dict[str, Dict[str, str]]:
        """컨텍스트별 프롬프트 템플릿 초기화"""
        return {
            "business": {
                "direct": """업무 환경에 적합한 직접적이고 명확한 톤으로 변환하세요.
- 핵심 메시지를 앞쪽에 배치
- 간결하고 구체적인 표현 사용
- 비즈니스 전문 용어 적절히 활용
- 결과 지향적인 표현""",
                
                "gentle": """업무 환경에서 부드럽고 협력적인 톤으로 변환하세요.
- 정중하면서도 친근한 어조
- 상대방을 배려하는 표현
- 제안이나 요청시 완곡한 표현 사용
- 팀워크를 강조하는 톤""",
                
                "neutral": """업무 환경에 적합한 중립적이고 전문적인 톤으로 변환하세요.
- 객관적이고 균형잡힌 표현
- 감정적 요소를 배제한 사실 중심
- 표준적인 비즈니스 커뮤니케이션 스타일
- 정확하고 명료한 전달"""
            },
            
            "report": {
                "direct": """보고서용 직접적이고 간결한 문체로 변환하세요.
- 결론부터 명시하는 구조
- 데이터와 사실 중심의 서술
- 군더더기 없는 명확한 표현
- 의사결정에 필요한 핵심 정보 강조""",
                
                "gentle": """보고서용이지만 읽기 쉽고 이해하기 편한 문체로 변환하세요.
- 논리적 흐름을 따르는 부드러운 전개
- 독자를 고려한 친화적 서술
- 복잡한 내용도 쉽게 풀어서 설명
- 적절한 예시나 부연설명 포함""",
                
                "neutral": """표준적인 보고서 문체로 변환하세요.
- 공식적이고 체계적인 구조
- 객관적 사실과 분석 중심
- 일관된 톤과 문체 유지
- 전문적이면서 이해하기 쉬운 표현"""
            },
            
            "personal": {
                "direct": """개인적 소통에서 솔직하고 직접적인 톤으로 변환하세요.
- 감정과 의견을 명확히 표현
- 솔직한 어조와 자연스러운 표현
- 개인적 경험이나 느낌 포함
- 진정성 있는 개성적 문체""",
                
                "gentle": """개인적 소통에서 따뜻하고 부드러운 톤으로 변환하세요.
- 상대방을 배려하는 따뜻한 어조
- 공감과 이해를 표현하는 문구
- 부드럽고 친근한 표현 방식
- 감정적 연결감을 주는 톤""",
                
                "neutral": """개인적 소통에서 자연스럽고 균형잡힌 톤으로 변환하세요.
- 너무 격식차리지도 너무 캐주얼하지도 않은 적절한 톤
- 상황에 맞는 적절한 감정 표현
- 자연스럽고 편안한 대화체
- 친밀감과 예의를 모두 고려한 표현"""
            }
        }
    
    def generate_user_negative_prompts(self, preferences: Dict[str, str]) -> str:
        """사용자 네거티브 선호도에 따른 맞춤 프롬프트 생성

        새 스키마(rhetoricLevel 등)와 레거시 키(avoidFloweryLanguage 등)를 모두 지원
        """
        user_negative_parts = []

        # 수사법/미사여구 수준 (새: rhetoricLevel = low/moderate/high)
        # 레거시: avoidFloweryLanguage = strict/moderate/lenient
        rhetoric = preferences.get("rhetoricLevel")
        flowery_level = preferences.get("avoidFloweryLanguage")
        if rhetoric:
            if rhetoric == "low":
                user_negative_parts.append("- 모든 형태의 미사여구, 꾸밈말, 과장된 표현을 완전히 배제")
            elif rhetoric == "moderate":
                user_negative_parts.append("- 과도한 미사여구나 불필요한 꾸밈말 사용 자제")
            elif rhetoric == "high":
                user_negative_parts.append("- 지나치게 과장된 표현만 피하고 적절한 수사법은 허용")
        elif flowery_level:
            if flowery_level == "strict":
                user_negative_parts.append("- 모든 형태의 미사여구, 꾸밈말, 과장된 표현을 완전히 배제")
            elif flowery_level == "moderate":
                user_negative_parts.append("- 과도한 미사여구나 불필요한 꾸밈말 사용 자제")
            elif flowery_level == "lenient":
                user_negative_parts.append("- 지나치게 과장된 표현만 피하고 적절한 수사법은 허용")

        # 반복 허용도 (새: repetitionTolerance = low/moderate/high)
        # 레거시: avoidRepetitiveWords = strict/moderate
        repetition = preferences.get("repetitionTolerance")
        repetitive_level = preferences.get("avoidRepetitiveWords")
        if repetition:
            if repetition == "low":
                user_negative_parts.append("- 동일하거나 유사한 단어/구문의 반복을 완전히 금지")
            elif repetition == "moderate":
                user_negative_parts.append("- 불필요한 단어나 구문 반복 최소화")
        elif repetitive_level:
            if repetitive_level == "strict":
                user_negative_parts.append("- 동일하거나 유사한 단어/구문의 반복을 완전히 금지")
            elif repetitive_level == "moderate":
                user_negative_parts.append("- 불필요한 단어나 구문 반복 최소화")

        # 문장부호 스타일 (새: punctuationStyle = minimal/standard/expressive)
        # 레거시: commaUsageStyle = strict/moderate
        punctuation = preferences.get("punctuationStyle")
        comma_style = preferences.get("commaUsageStyle")
        if punctuation:
            if punctuation == "minimal":
                user_negative_parts.append("- 쉼표 사용을 최소한으로 제한, 꼭 필요한 경우만 사용")
            elif punctuation == "standard":
                user_negative_parts.append("- 과도한 쉼표 남발 피하기")
        elif comma_style:
            if comma_style == "strict":
                user_negative_parts.append("- 쉼표 사용을 최소한으로 제한, 꼭 필요한 경우만 사용")
            elif comma_style == "moderate":
                user_negative_parts.append("- 과도한 쉼표 남발 피하기")

        # 내용 초점 (새: contentFocus = content/balanced/format)
        # 레거시: contentOverFormat = strict/moderate
        content_focus = preferences.get("contentFocus") or preferences.get("contentOverFormat")
        if content_focus in ("content", "strict"):
            user_negative_parts.append("- 형식적 구조보다 내용과 의미 전달에 절대 우선순위")
        elif content_focus in ("balanced", "moderate"):
            user_negative_parts.append("- 형식에 치중하여 내용이 빈약해지는 것 방지")

        # 불릿 포인트 사용 (새: bulletPreference = avoid/minimal/prefer)
        # 레거시: bulletPointUsage = strict/moderate
        bullet_pref = preferences.get("bulletPreference") or preferences.get("bulletPointUsage")
        if bullet_pref in ("avoid", "strict"):
            user_negative_parts.append("- 불렛 포인트나 리스트 형태 완전 금지")
        elif bullet_pref in ("minimal", "moderate"):
            user_negative_parts.append("- 과도한 불렛 포인트나 리스트 형태 사용 제한")

        # 이모티콘 정책 (새: emoticonPolicy = none/minimal/contextual/frequent)
        # 레거시: emoticonUsage = strict/moderate
        emoticon_policy = preferences.get("emoticonPolicy")
        emoticon_usage = preferences.get("emoticonUsage")
        if emoticon_policy:
            if emoticon_policy == "none":
                user_negative_parts.append("- 모든 이모티콘, 이모지, 특수문자 완전 배제")
            elif emoticon_policy in ("minimal", "contextual"):
                user_negative_parts.append("- 이모티콘이나 특수문자 남용 금지")
        elif emoticon_usage:
            if emoticon_usage == "strict":
                user_negative_parts.append("- 모든 이모티콘, 이모지, 특수문자 완전 배제")
            elif emoticon_usage == "moderate":
                user_negative_parts.append("- 이모티콘이나 특수문자 남용 금지")

        # 커스텀 네거티브 프롬프트 (레거시 지원)
        custom_prompts = preferences.get('customNegativePrompts', [])
        if isinstance(custom_prompts, list) and custom_prompts:
            user_negative_parts.extend([f"- {prompt}" for prompt in custom_prompts])

        if user_negative_parts:
            return "\n추가 사용자 맞춤 제한사항:\n" + "\n".join(user_negative_parts)
        return ""
    
    def _generate_enterprise_prompt_part(self, enterprise_context: Optional[Dict[str, Any]]) -> str:
        """기업 컨텍스트를 프롬프트의 일부로 변환"""
        if not enterprise_context:
            return ""

        parts = []
        # enterprise_context 딕셔너리를 순회하며 프롬프트 문자열 생성
        for key, value in enterprise_context.items():
            # 값이 리스트인 경우 각 항목을 불렛 포인트로 처리
            if isinstance(value, list):
                items = "\n".join([f"- {item}" for item in value])
                parts.append(f"기업 {key}:\n{items}")
            # 값이 리스트가 아닌 경우 단순 키-값 형태로 처리
            else:
                parts.append(f"기업 {key}: {value}")

        # 생성된 부분이 있을 경우 제목과 함께 최종 문자열 반환
        if parts:
            return ("\n기업별 가이드라인:\n" + "\n".join(parts) +
                    "\n\n위 가이드라인에서 인용할 때는 [문서 N] 형식으로 출처를 표기하세요.\n")
        return ""

    
    def generate_conversion_prompts(self, user_profile: Dict[str, Any], 
                                   context: str, 
                                    enterprise_context: Optional[Dict[str, Any]] = None,
                                   negative_preferences: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """사용자 프로필과 컨텍스트에 따른 변환 프롬프트 생성"""
        
        # 사용자 스타일 레벨 추출 (세션 레벨 우선, 없으면 기본 레벨)
        formality_level = user_profile.get('sessionFormalityLevel', 
                                          user_profile.get('baseFormalityLevel', 3))
        friendliness_level = user_profile.get('sessionFriendlinessLevel',
                                             user_profile.get('baseFriendlinessLevel', 3))
        emotion_level = user_profile.get('sessionEmotionLevel',
                                        user_profile.get('baseEmotionLevel', 3))
        directness_level = user_profile.get('sessionDirectnessLevel',
                                           user_profile.get('baseDirectnessLevel', 3))
        
        # 기본 사용자 특성 프롬프트
        user_characteristics = f"""
사용자 스타일 특성:
- 격식도: {formality_level}/10 (1=매우 캐주얼, 10=매우 격식)
- 친근함: {friendliness_level}/10 (1=차가운, 10=매우 친근)
- 감정표현: {emotion_level}/10 (1=건조한, 10=감정적)
- 직설성: {directness_level}/10 (1=돌려서, 10=직접적)
"""
        # 기업별 가이드라인 프롬프트 생성
        enterprise_guidelines = self._generate_enterprise_prompt_part(enterprise_context)
        
        # 기본 네거티브 프롬프트
        base_negative = self.base_negative_prompts.get("common", "")
        context_negative = self.base_negative_prompts.get(context, "")
        
        # 사용자 맞춤 네거티브 프롬프트
        user_negative = ""
        if negative_preferences:
            user_negative = self.generate_user_negative_prompts(negative_preferences)
        
        # 통합 네거티브 프롬프트
        combined_negative = f"{base_negative}\n{context_negative}{user_negative}"
        
        # 컨텍스트별 프롬프트 템플릿 가져오기
        context_templates = self.context_specific_prompts.get(context, 
                                                             self.context_specific_prompts["personal"])
        
        # 스타일별 한국어 이름 및 설명
        style_meta = {
            "direct": {
                "name": "직접적 (Direct)",
                "desc": "핵심을 명확하게 전달하는 직접적이고 간결한 말투",
                "goal": "돌려 말하지 않고 핵심을 바로 전달",
            },
            "gentle": {
                "name": "부드러운 (Gentle)",
                "desc": "상대방을 배려하는 따뜻하고 부드러운 말투",
                "goal": "상대방이 편안하게 느낄 수 있도록 완곡하게 전달",
            },
            "neutral": {
                "name": "중립적 (Neutral)",
                "desc": "감정을 배제한 객관적이고 균형 잡힌 말투",
                "goal": "감정 없이 사실과 요청을 담백하게 전달",
            },
        }

        # 스타일 변환 프롬프트 (direct, gentle, neutral)
        prompts = {}
        for style in ['direct', 'gentle', 'neutral']:
            meta = style_meta[style]
            style_template = context_templates.get(style, "")

            prompts[style] = f"""역할: 당신은 사용자의 말투를 **{meta['name']}** 스타일로 변환하는 커뮤니케이션 코치입니다.
변환 목표: {meta['desc']}

핵심 규칙:
- 원본 텍스트의 **의미, 내용, 의도를 그대로 유지**하세요.
- 절대로 입력 텍스트에 대한 답변, 반응, 공감, 조언을 하지 마세요.
- 입력이 "화가 난 표현"이면 → 같은 내용을 다른 말투로 표현하세요.
- 입력이 "질문"이면 → 같은 질문을 다른 말투로 표현하세요.

{user_characteristics}
{enterprise_guidelines}
{style_template}

처리 절차:
1. **입력 분석**: 현재 말투, 톤, 어조를 파악합니다.
2. **문제점 파악**: {meta['name']} 스타일 관점에서 현재 입력의 개선이 필요한 부분을 찾습니다.
3. **개선 안내**: 왜 고쳐야 하는지 이유를 설명합니다.
4. **요약 & 변환**: 최종 변환 문장을 제시합니다.

출력 형식 (반드시 이 마크다운 형식을 따르세요):

### 입력 분석

| 항목 | 분석 |
|------|------|
| 현재 말투 | (캐주얼/반말/존댓말/명령조 등) |
| 톤/어조 | (공격적/친근/무관심/급함 등) |
| 격식 수준 | N/10 |

### 개선 포인트
- **[포인트 1]**: "현재 표현"은 ~한 인상을 줄 수 있으므로, ~하게 바꾸시는 것이 좋습니다.
- **[포인트 2]**: ...
(기업 가이드라인이 있으면 [문서 N]으로 근거를 인용하세요)

### 요약
> 사용자의 입력은 "{{원문 핵심 요약}}"인데, **{meta['name']}** 스타일에 맞추면 "{{변환 핵심 요약}}"으로 표현하시는 것이 좋습니다. {meta['goal']}이/가 핵심입니다.

(기업 가이드라인이 있는 경우 아래 문장을 추가하세요)
> 귀사의 가이드라인([문서 N])에 따르면, ~하는 것이 권장됩니다.

## 완성된 변환 문장
{{변환된 최종 문장만 작성}}

{combined_negative}

주의사항:
- 설명은 사용자에게 직접 말하는 코칭 어조로 작성하세요 (~하시는 것이 좋습니다).
- ## 완성된 변환 문장 마크다운 헤더 뒤에는 반드시 변환된 문장만 작성하세요.
"""

        # 문법 교정 프롬프트
        prompts['grammar'] = f"""당신은 한국어 문법 교정 전문가이자 글쓰기 코치입니다.

당신의 역할:
사용자가 입력한 텍스트에서 문법적으로 잘못된 부분을 찾아내고, 왜 잘못되었는지 설명한 뒤, 올바르게 교정한 최종 문장을 제시합니다.
**사용자에게 왜 이렇게 고쳐야 하는지 이유를 친절하게 안내하는 코칭 역할**도 합니다.

{user_characteristics}
{enterprise_guidelines}

분석 절차:
1. 원본 텍스트에서 맞춤법, 띄어쓰기, 문법 오류를 찾으세요.
2. 각 오류에 대해 어떤 부분이 잘못되었는지 **볼드체**로 표시하세요.
3. 왜 잘못되었는지 간결하게 이유를 설명하세요.
4. 올바른 표현을 제안하세요.
5. 모든 교정을 반영한 최종 완성 문장을 제시하세요.

출력 형식 (반드시 이 형식을 따르세요):

### 문법 분석

(오류가 있는 경우)
| 원본 표현 | 문제점 | 수정 제안 |
|-----------|--------|-----------|
| **잘못된부분** | 이유 설명 | 올바른 표현 |

(오류가 없는 경우)
문법적으로 올바른 문장입니다.

### 이렇게 고치셔야 하는 이유
- 각 교정 항목마다 **왜 이 표현이 틀렸는지**, **올바른 규칙이 무엇인지** 구체적으로 설명하세요.
- "~은/는 ~규칙에 따라 ~로 쓰셔야 합니다" 형식으로 안내하세요.
- 예시: "'안그러면'은 '안'과 '그러면'이 별개의 단어이므로 띄어서 '안 그러면'으로 쓰셔야 합니다."
- 예시: "'큰일남'에서 '큰일'과 '나다'는 별개의 단어이므로 '큰일 남' 또는 '큰일 나'로 띄어 쓰셔야 합니다."

## 완성된 변환 문장
{{교정이 모두 반영된 최종 문장}}

주의사항:
- 원본의 의미와 의도는 절대 변경하지 마세요.
- 문법 교정만 하세요. 스타일이나 톤 변환은 하지 마세요.
- 비속어나 은어가 있어도 의미는 유지하되, 문법적 오류만 수정하세요.
- 구어체/줄임말이 의도적 표현인 경우 지적하되 강제 수정하지 마세요 (참고사항으로 언급).
- 설명은 사용자에게 직접 말하는 코칭 어조로 작성하세요 (~하셔야 합니다, ~하시는 것이 좋습니다).
- ## 완성된 변환 문장 마크다운 헤더 뒤에는 반드시 교정된 문장만 작성하세요.
"""

        # 격식도(Formality) 분석 프롬프트
        prompts['formality'] = f"""당신은 한국어 격식도(포멀리티) 분석 전문가이자 커뮤니케이션 코치입니다.

당신의 역할:
사용자가 입력한 텍스트의 격식도를 분석하고, 상황에 맞는 격식 수준으로 변환합니다.
**사용자에게 왜 이렇게 고쳐야 하는지 이유를 친절하게 안내하는 코칭 역할**도 합니다.

{user_characteristics}
{enterprise_guidelines}

분석 절차:
1. 원본 텍스트의 현재 격식 수준을 판단하세요 (1=매우 캐주얼 ~ 10=매우 격식).
2. 사용자의 격식도 설정({formality_level}/10)에 맞춰 변환 방향을 결정하세요.
3. 높임법, 종결어미, 호칭, 어휘 수준을 조정하세요.
4. 기업 가이드라인이 있으면 해당 기준을 우선 적용하고 [문서 N]으로 인용하세요.

출력 형식 (반드시 이 형식을 따르세요):

### 귀사 가이드라인 안내
(기업 가이드라인이 있는 경우 — 이 섹션을 **가장 먼저** 출력하세요)
- "귀사의 [문서 제목]([문서 N])에 따르면, ~해야 합니다." 형식으로 관련 지침을 요약하세요.
- 격식도와 관련된 기업 규정(높임법, 호칭, 어휘 수준 등)을 먼저 안내하세요.
- 예시: "귀사의 이메일 작성 가이드라인([문서 2])에 따르면, 사내 커뮤니케이션에서는 정중한 요청 형식과 높임법을 사용해야 합니다."

(기업 가이드라인이 없는 경우)
이 섹션을 생략하고 바로 격식도 분석으로 넘어가세요.

### 격식도 분석

| 항목 | 현재 수준 | 목표 수준 | 조정 내용 |
|------|-----------|-----------|-----------|
| 높임법 | 현재 상태 | 목표 상태 | 변경사항 |
| 종결어미 | 현재 상태 | 목표 상태 | 변경사항 |
| 어휘 수준 | 현재 상태 | 목표 상태 | 변경사항 |

### 이렇게 고치셔야 하는 이유
- 각 조정 항목마다 **왜 현재 표현이 부적절한지**, **어떤 상황에서 문제가 될 수 있는지** 구체적으로 설명하세요.
- "~하면 ~로 오해받을 수 있으므로, ~하게 바꾸시는 것이 좋습니다" 형식으로 안내하세요.
- 기업 가이드라인이 있으면 "[문서 N]에 따르면 ~해야 합니다"로 근거를 제시하세요.
- 예시: "반말 종결어미('~줘')는 상사나 고객에게 무례하게 들릴 수 있으므로, '~해 주시기 바랍니다'로 바꾸시는 것이 좋습니다."

## 완성된 변환 문장
{{격식도가 조정된 최종 문장}}

{combined_negative}

주의사항:
- 원본의 의미와 의도는 절대 변경하지 마세요.
- 격식 수준 조정만 하세요. 내용이나 논지를 바꾸지 마세요.
- 기업 가이드라인이 있다면 반드시 참조하고 출처를 표기하세요.
- 설명은 사용자에게 직접 말하는 코칭 어조로 작성하세요 (~하셔야 합니다, ~하시는 것이 좋습니다).
- ## 완성된 변환 문장 마크다운 헤더 뒤에는 반드시 변환된 문장만 작성하세요.
"""

        # 프로토콜(Protocol) 분석 프롬프트
        prompts['protocol'] = f"""당신은 한국어 커뮤니케이션 프로토콜 전문가이자 비즈니스 매너 코치입니다.

당신의 역할:
사용자가 입력한 텍스트가 비즈니스/조직 커뮤니케이션 프로토콜에 맞는지 분석하고, 위반 사항을 수정합니다.
**사용자에게 왜 이렇게 고쳐야 하는지 이유와 근거를 친절하게 안내하는 코칭 역할**도 합니다.

{user_characteristics}
{enterprise_guidelines}

분석 절차:
1. 원본 텍스트에서 커뮤니케이션 프로토콜 위반 사항을 찾으세요.
2. 각 위반에 대해 어떤 프로토콜이 위반되었는지 설명하세요.
3. 기업 가이드라인이 있으면 해당 규정을 [문서 N] 형식으로 인용하세요.
4. 프로토콜에 맞게 수정된 최종 문장을 제시하세요.

검사 항목:
- 인사말/맺음말 프로토콜 (상황에 맞는 적절한 인사)
- 호칭 프로토콜 (직급, 존칭 적절성)
- 요청/지시 프로토콜 (적절한 요청 형식)
- 보고 프로토콜 (결론 우선, 핵심 요약)
- CC/수신자 적절성 안내

출력 형식 (반드시 이 형식을 따르세요):

### 귀사 가이드라인 안내
(기업 가이드라인이 있는 경우 — 이 섹션을 **가장 먼저** 출력하세요)
- "귀사의 [문서 제목]([문서 N])에 따르면, ~해야 합니다." 형식으로 관련 지침을 요약하세요.
- 프로토콜과 관련된 기업 규정(인사말, 호칭, 요청 형식, 보고 형식 등)을 먼저 안내하세요.
- 예시: "귀사의 이메일 작성 가이드라인([문서 2])에 따르면, 이메일에는 반드시 인사말을 포함하고, 요청 시 정중한 표현을 사용해야 합니다. 또한 비즈니스 스타일 가이드([문서 3])에서는 불필요한 감정 표현을 제거하라고 안내하고 있습니다."

(기업 가이드라인이 없는 경우)
이 섹션을 생략하고 바로 프로토콜 분석으로 넘어가세요.

### 프로토콜 분석

(위반 사항이 있는 경우)
| 위반 항목 | 현재 표현 | 위반 프로토콜 | 수정 제안 |
|-----------|-----------|---------------|-----------|
| 항목명 | **현재 표현** | 관련 규정 [문서 N] | 수정된 표현 |

(위반 사항이 없는 경우)
커뮤니케이션 프로토콜을 준수하고 있습니다.

### 이렇게 고치셔야 하는 이유
- 각 위반 항목마다 **왜 현재 표현이 프로토콜에 맞지 않는지**, **이대로 보내면 어떤 문제가 생길 수 있는지** 구체적으로 설명하세요.
- "~하시면 ~로 비춰질 수 있으므로, ~하시는 것이 좋습니다" 형식으로 안내하세요.
- 기업 가이드라인이 있으면 "[문서 N]에 따르면 ~해야 합니다"로 근거를 제시하세요.
- 예시: "인사말 없이 바로 요청하시면 상대방이 일방적이라고 느낄 수 있으므로, '안녕하세요, OOO님'으로 시작하시는 것이 좋습니다. [문서 2] 이메일 가이드라인에서도 인사말을 필수로 안내하고 있습니다."

## 완성된 변환 문장
{{프로토콜이 반영된 최종 문장}}

{combined_negative}

주의사항:
- 원본의 의미와 의도는 절대 변경하지 마세요.
- 프로토콜 준수 여부만 분석하세요. 문법이나 스타일은 변경하지 마세요.
- 기업 가이드라인 문서가 있으면 반드시 [문서 N] 형식으로 출처를 인용하세요.
- 기업 가이드라인이 없는 경우, 일반적인 비즈니스 커뮤니케이션 관례에 따라 분석하세요.
- 설명은 사용자에게 직접 말하는 코칭 어조로 작성하세요 (~하셔야 합니다, ~하시는 것이 좋습니다).
- ## 완성된 변환 문장 마크다운 헤더 뒤에는 반드시 변환된 문장만 작성하세요.
"""

        return prompts
