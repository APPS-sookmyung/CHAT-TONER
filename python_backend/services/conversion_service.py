"""
텍스트 변환 통합 서비스
프롬프트 엔지니어링과 OpenAI API를 연결하는 메인 서비스

전체 텍스트 스타일 변환 프로세스를 통합하는 메인 서비스 클래스
> gpt 보낼 프롬프트 생성
> OpenAI API 호출로 텍스트 변환
> 변환된 텍스트와 메타데이터 반환
> 사용자 피드백 처리 및 프로필 업데이트
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .prompt_engineering import PromptEngineer
from .openai_services import OpenAIService

logger = logging.getLogger('chattoner.conversion_service')

class ConversionService:
    """텍스트 변환 메인 서비스 클래스"""

    def __init__(self, prompt_engineer=None, openai_service=None):
        self.prompt_engineer = prompt_engineer or PromptEngineer()
        self.openai_service = openai_service or OpenAIService()
        self.logger = logger
    
    async def convert_text(self,
                          input_text: str,
                          user_profile: Dict[str, Any],
                          context: str = "personal",
                          negative_preferences: Optional[Dict[str, str]] = None,
                          enterprise_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        메인 텍스트 변환 함수

        Args:
            input_text: 변환할 원본 텍스트
            user_profile: 사용자 스타일 프로필
            context: 변환 컨텍스트 ("business", "report", "personal")
            negative_preferences: 사용자 네거티브 프롬프트 선호도
            enterprise_context: 기업 컨텍스트 정보 (옵션)

        Returns:
            변환 결과와 메타데이터
        """
        # 입력 검증
        if not input_text or not input_text.strip():
            self.logger.warning("빈 텍스트 변환 시도")
            return self._create_error_response("입력 텍스트가 비어있습니다", input_text)

        if not user_profile:
            self.logger.warning("사용자 프로필 없이 변환 시도")
            user_profile = {}

        try:
            self.logger.info(f"텍스트 변환 시작: context={context}, length={len(input_text)}")

            # 1. 프롬프트 생성
            try:
                prompts = self.prompt_engineer.generate_conversion_prompts(
                    user_profile=user_profile,
                    context=context,
                    enterprise_context=enterprise_context,
                    negative_preferences=negative_preferences
                )
                self.logger.debug(f"프롬프트 생성 완료: {list(prompts.keys())}")
            except Exception as e:
                self.logger.error(f"프롬프트 생성 실패: {e}", exc_info=True)
                raise ValueError(f"프롬프트 생성 중 오류 발생: {str(e)}")

            # 2. OpenAI API 호출하여 텍스트 변환
            try:
                converted_texts = await self.openai_service.convert_text_styles(
                    input_text=input_text,
                    prompts=prompts
                )
                self.logger.debug("텍스트 변환 완료")
            except Exception as e:
                self.logger.error(f"OpenAI 텍스트 변환 실패: {e}", exc_info=True)
                raise RuntimeError(f"텍스트 변환 API 호출 실패: {str(e)}")

            # 3. 원본 텍스트 감정 분석 (실패해도 계속 진행)
            sentiment_analysis = None
            try:
                sentiment_analysis = await self.openai_service.analyze_sentiment(input_text)
            except Exception as e:
                self.logger.warning(f"감정 분석 실패 (무시하고 계속): {e}")
                sentiment_analysis = {"rating": 3, "confidence": 0.0}

            # 4. 결과 구성
            result = {
                "success": True,
                "original_text": input_text,
                "converted_texts": converted_texts,
                "context": context,
                "user_profile": user_profile,
                "sentiment_analysis": sentiment_analysis,
                "metadata": {
                    "prompts_used": list(prompts.keys()),
                    "conversion_timestamp": self._get_timestamp(),
                    "model_used": self.openai_service.model
                }
            }

            self.logger.info("텍스트 변환 성공")
            return result

        except ValueError as e:
            # 입력 검증 오류 (4xx 에러로 처리)
            self.logger.warning(f"입력 검증 실패: {e}")
            return self._create_error_response(str(e), input_text)

        except RuntimeError as e:
            # API 호출 오류 (5xx 에러로 처리)
            self.logger.error(f"서비스 실행 오류: {e}", exc_info=True)
            return self._create_error_response(str(e), input_text)

        except Exception as e:
            # 예상치 못한 오류
            self.logger.critical(f"텍스트 변환 중 예상치 못한 오류: {e}", exc_info=True)
            return self._create_error_response("서버 내부 오류가 발생했습니다", input_text)
    
    async def process_user_feedback(self,
                                   feedback_text: str,
                                   user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 피드백 처리 및 프로필 업데이트

        Args:
            feedback_text: 사용자 피드백
            user_profile: 현재 사용자 프로필

        Returns:
            업데이트된 사용자 프로필과 피드백 분석 결과
        """
        # 입력 검증
        if not feedback_text or not feedback_text.strip():
            self.logger.warning("빈 피드백 텍스트 처리 시도")
            return {
                "success": False,
                "error": "피드백 텍스트가 비어있습니다",
                "updated_profile": user_profile
            }

        if not user_profile:
            self.logger.error("사용자 프로필 없이 피드백 처리 시도")
            return {
                "success": False,
                "error": "사용자 프로필이 필요합니다",
                "updated_profile": {}
            }

        try:
            self.logger.info(f"피드백 처리 시작: length={len(feedback_text)}")

            # 피드백 분석
            try:
                style_deltas = await self.openai_service.analyze_style_feedback(feedback_text)
                self.logger.debug(f"스타일 델타 분석 완료: {style_deltas}")
            except Exception as e:
                self.logger.error(f"피드백 분석 실패: {e}", exc_info=True)
                raise RuntimeError(f"피드백 분석 중 오류 발생: {str(e)}")

            # 사용자 프로필 업데이트 (세션 레벨)
            updated_profile = user_profile.copy()

            # 기존 값에 델타 적용 (1-10 범위로 제한)
            current_formality = updated_profile.get('sessionFormalityLevel',
                                                  updated_profile.get('baseFormalityLevel', 3))
            current_friendliness = updated_profile.get('sessionFriendlinessLevel',
                                                     updated_profile.get('baseFriendlinessLevel', 3))
            current_emotion = updated_profile.get('sessionEmotionLevel',
                                                updated_profile.get('baseEmotionLevel', 3))
            current_directness = updated_profile.get('sessionDirectnessLevel',
                                                   updated_profile.get('baseDirectnessLevel', 3))

            updated_profile['sessionFormalityLevel'] = max(1, min(10,
                current_formality + style_deltas.get('formalityDelta', 0) * 2))
            updated_profile['sessionFriendlinessLevel'] = max(1, min(10,
                current_friendliness + style_deltas.get('friendlinessDelta', 0) * 2))
            updated_profile['sessionEmotionLevel'] = max(1, min(10,
                current_emotion + style_deltas.get('emotionDelta', 0) * 2))
            updated_profile['sessionDirectnessLevel'] = max(1, min(10,
                current_directness + style_deltas.get('directnessDelta', 0) * 2))

            self.logger.info("피드백 처리 성공")
            return {
                "success": True,
                "updated_profile": updated_profile,
                "style_adjustments": style_deltas,
                "feedback_processed": feedback_text
            }

        except RuntimeError as e:
            self.logger.error(f"피드백 처리 실패: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "updated_profile": user_profile
            }

        except Exception as e:
            self.logger.critical(f"피드백 처리 중 예상치 못한 오류: {e}", exc_info=True)
            return {
                "success": False,
                "error": "서버 내부 오류가 발생했습니다",
                "updated_profile": user_profile
            }

    def _create_error_response(self, error_message: str, input_text: str) -> Dict[str, Any]:
        """에러 응답 생성 헬퍼 메서드"""
        return {
            "success": False,
            "error": error_message,
            "original_text": input_text,
            "converted_texts": {
                "direct": input_text,
                "gentle": input_text,
                "neutral": input_text
            }
        }

    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
