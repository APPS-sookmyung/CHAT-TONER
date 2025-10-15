"""
OpenAI API 서비스
텍스트 스타일 변환을 위한 OpenAI GPT 모델 호출
"""

import os
import logging
from typing import Dict, List, Any
from openai import OpenAI, OpenAIError, APIError, APIConnectionError, RateLimitError
import json

logger = logging.getLogger('chattoner.openai_service')

class OpenAIService:
    """OpenAI API 호출 관리 클래스"""

    def __init__(self, api_key=None, model=None):
        # 설정에서 API 키를 가져오거나 직접 환경변수에서 가져옴
        from core.config import get_settings
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.logger = logger

        # API 키가 없거나 placeholder인 경우 Mock 모드로 동작
        if not self.api_key or self.api_key == "your-openai-api-key-here":
            self.logger.warning("OpenAI API key not found. Running in mock mode.")
            self.client = None
            self.mock_mode = True
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.mock_mode = False
                self.logger.info(f"OpenAI client initialized successfully with model: {self.model}")
            except Exception as e:
                self.logger.error(f"OpenAI client initialization failed: {e}. Running in mock mode.", exc_info=True)
                self.client = None
                self.mock_mode = True
    async def convert_text_styles(self, input_text: str, prompts: Dict[str, str]) -> Dict[str, str]:
        """
        입력 텍스트를 3가지 스타일로 변환

        Args:
            input_text: 변환할 원본 텍스트
            prompts: 각 스타일별 프롬프트 딕셔너리

        Returns:
            3가지 스타일 변환 결과 딕셔너리

        Raises:
            ValueError: 입력값이 유효하지 않은 경우
            RuntimeError: OpenAI API 호출 실패 시
        """
        # 입력 검증
        if not input_text or not input_text.strip():
            raise ValueError("입력 텍스트가 비어있습니다")

        if not prompts:
            raise ValueError("프롬프트가 제공되지 않았습니다")

        results = {}

        try:
            self.logger.info(f"스타일 변환 시작: {len(prompts)}개 스타일")

            # Direct 스타일 변환
            if 'direct' in prompts:
                results['direct'] = await self._convert_single_style(
                    input_text, prompts['direct'], 'direct'
                )

            # Gentle 스타일 변환
            if 'gentle' in prompts:
                results['gentle'] = await self._convert_single_style(
                    input_text, prompts['gentle'], 'gentle'
                )

            # Neutral 스타일 변환
            if 'neutral' in prompts:
                results['neutral'] = await self._convert_single_style(
                    input_text, prompts['neutral'], 'neutral'
                )

            self.logger.info(f"스타일 변환 완료: {len(results)}개 결과")
            return results

        except (ValueError, RuntimeError):
            # 예상된 에러는 재발생
            raise

        except Exception as e:
            self.logger.critical(f"예상치 못한 스타일 변환 오류: {e}", exc_info=True)
            raise RuntimeError(f"스타일 변환 중 내부 오류 발생: {str(e)}")
    
    async def _convert_single_style(self, input_text: str, prompt: str, style_name: str = "unknown") -> str:
        """
        단일 스타일 변환 수행

        Args:
            input_text: 변환할 텍스트
            prompt: 변환에 사용할 프롬프트
            style_name: 스타일 이름 (로깅용)

        Returns:
            변환된 텍스트

        Raises:
            RuntimeError: API 호출 실패 시
        """
        if self.mock_mode:
            self.logger.debug(f"Mock mode: {style_name} 스타일 변환 스킵")
            return f"[Mock] {input_text}"

        try:
            self.logger.debug(f"{style_name} 스타일 변환 시작")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"다음 텍스트를 변환해주세요:\n\n{input_text}"
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )

            converted_text = response.choices[0].message.content.strip()
            self.logger.debug(f"{style_name} 스타일 변환 완료: {len(converted_text)}자")
            return converted_text

        except RateLimitError as e:
            self.logger.error(f"OpenAI API 요청 한도 초과 ({style_name}): {e}")
            raise RuntimeError(f"API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")

        except APIConnectionError as e:
            self.logger.error(f"OpenAI API 연결 실패 ({style_name}): {e}")
            raise RuntimeError(f"API 서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.")

        except APIError as e:
            self.logger.error(f"OpenAI API 오류 ({style_name}): {e}", exc_info=True)
            raise RuntimeError(f"API 서버 오류가 발생했습니다: {str(e)}")

        except Exception as e:
            self.logger.critical(f"{style_name} 스타일 변환 중 예상치 못한 오류: {e}", exc_info=True)
            raise RuntimeError(f"텍스트 변환 중 내부 오류 발생: {str(e)}")
    
    #사용자 텍스트의 감정을 수치화 (15점, 신뢰도 01).
    #결과는 JSON 형태로 요청하고, 이를 파싱하여 반환.
    #예외 시 기본값 3점 / 0.5 신뢰도 반환.


    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        텍스트 감정 분석
        
        Args:
            text: 분석할 텍스트
        
        Returns:
            감정 분석 결과 (rating, confidence)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 감정 분석 전문가입니다. 
                        텍스트의 감정을 분석하여 1-5점 평점과 0-1 신뢰도를 제공하세요.
                        응답은 JSON 형식으로: {"rating": number, "confidence": number}"""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=100,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            parsed_result = json.loads(result)
            
            return {
                "rating": max(1, min(5, round(parsed_result.get("rating", 3)))),
                "confidence": max(0, min(1, parsed_result.get("confidence", 0.5)))
            }
            
        except Exception as e:
            print(f"감정 분석 오류: {e}")
            return {"rating": 3, "confidence": 0.5}
    
    def analyze_style_feedback(self, feedback_text: str) -> Dict[str, float]:
        """
        사용자 피드백을 분석하여 스타일 조정값 계산
        
        Args:
            feedback_text: 사용자 피드백 텍스트
        
        Returns:
            스타일 조정값 딕셔너리
        """
        try: # 격식, 친근함, 감정, 직설성을 조정함. 
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """사용자 피드백을 분석하여 스타일 조정값을 계산하세요.
                        다음 JSON 형식으로 응답: 
                        {
                            "formalityDelta": float (-1.0 to 1.0),
                            "friendlinessDelta": float (-1.0 to 1.0), 
                            "emotionDelta": float (-1.0 to 1.0),
                            "directnessDelta": float (-1.0 to 1.0)
                        }
                        
                        피드백 분석 기준:
                        - "더 격식있게", "공식적으로" → formalityDelta 양수
                        - "더 친근하게", "부드럽게" → friendlinessDelta 양수  
                        - "더 감정적으로", "따뜻하게" → emotionDelta 양수
                        - "더 직설적으로", "명확하게" → directnessDelta 양수
                        """
                    },
                    {
                        "role": "user",
                        "content": feedback_text # 피드백 텍스트를 입력
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"피드백 분석 오류: {e}")
            return {
                "formalityDelta": 0.0,
                "friendlinessDelta": 0.0, 
                "emotionDelta": 0.0,
                "directnessDelta": 0.0
            }