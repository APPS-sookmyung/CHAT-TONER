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
    
    def generate_conversion_prompts(self, user_profile: Dict[str, Any], 
                                   context: str, 
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
        
        # 각 스타일별 프롬프트 생성
        prompts = {}
        for style in ['direct', 'gentle', 'neutral']:
            style_template = context_templates.get(style, "")
            
            prompts[style] = f"""
{user_characteristics}

{style_template}

{combined_negative}

변환 시 위의 사용자 특성과 제한사항을 모두 고려하여 자연스럽고 개성있는 한국어로 변환해주세요.
"""
        
        return prompts
