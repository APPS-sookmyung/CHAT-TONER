"""
LoRA 파인튜닝 모델을 활용한 공식 문서 변환 체인 - HTTP 클라이언트 버전
공적인 말투 변환 시 런팟 추론 서버 1차 변환 후 ChatGPT 2차 다듬기 적용

주요 기능:
- 런팟 추론 서버 HTTP 요청
- 사용자 프로필과 컨텍스트 기반 공식 문서 변환 조건 판단
- 런팟 서버를 통한 1차 공식 말투 변환
- ChatGPT를 통한 2차 다듬기 및 보완
- Services와 동일한 구조로 프롬프트 엔지니어링 통합
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import httpx

# 프로젝트 경로 설정
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 로거 설정
logger = logging.getLogger(__name__)

class FinetuneChain:
    """LoRA 파인튜닝 모델을 활용한 공식 문서 변환 체인"""
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.3,
        prompt_engineer: Optional[object] = None,
        openai_service: Optional[object] = None,
    ):
        """Finetune Chain 초기화"""
        dotenv_path = Path(__file__).resolve().parents[3] / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        # 런팟 추론 서버 URL 설정
        from core.config import get_settings
        settings = get_settings()
        self.inference_url = settings.FINETUNE_URL
        
        # Services 초기화 (DI 우선, 없으면 내부 생성)
        try:
            if prompt_engineer is None or openai_service is None:
                from services.prompt_engineering import PromptEngineer
                from services.openai_services import OpenAIService
                self.prompt_engineer = prompt_engineer or PromptEngineer()
                self.openai_service = openai_service or OpenAIService()
            else:
                self.prompt_engineer = prompt_engineer
                self.openai_service = openai_service
            self.services_available = True
            logger.info("Services 초기화 완료")
        except ImportError as e:
            self.services_available = False
            logger.warning(f"Services import 실패: {e}")
        except Exception as e:
            self.services_available = False
            logger.error(f"Services 인스턴스 생성 실패: {e}")
     
        # 런팟 서버 연결 상태 확인
        self.is_inference_server_available = self._check_inference_server()
    
    def _check_inference_server(self) -> bool:
        """런팟 추론 서버 연결 상태 확인"""
        try:
            response = httpx.get(f"{self.inference_url}/health", timeout=5.0)
            if response.status_code == 200:
                logger.info("런팟 추론 서버 연결 성공")
                return True
            else:
                logger.warning(f"런팟 추론 서버 응답 오류: {response.status_code}")
                return False
        except httpx.HTTPError as e:
            logger.warning(f"런팟 추론 서버 연결 실패: {e}")
            return False
    
    def _should_use_lora(self, user_profile: Dict, context: str) -> bool:
        """공식 문서 변환 필요 여부 판단"""
        # 1. 직접적인 공식 문서 모드
        if user_profile.get('formal_document_mode', False):
            return True
        
        # 2. 격식도 기반 판단
        formality_level = user_profile.get('sessionFormalityLevel', 
                                          user_profile.get('baseFormalityLevel', 3))
        
        # 격식도가 5 이상
        if formality_level >= 5:
            return True
        
        # 격식도 4 이상 & business/report 컨텍스트
        if formality_level >= 4 and context in ["business", "report"]:
            return True
        
        return False
    
    async def _generate_with_lora(self, input_text: str, max_tokens: int = 256) -> str:
        """런팟 추론 서버로 1차 변환"""
        if not self.is_inference_server_available:
            raise Exception("런팟 추론 서버에 연결할 수 없습니다.")
        
        try:
            # 런팟 추론 서버로 HTTP 요청
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.inference_url}/generate",
                    json={
                        "prompt": input_text,
                        "max_new_tokens": max_tokens,
                        "temperature": 0.7,
                        "do_sample": True,
                    },
                )
                response.raise_for_status()
                result = response.json()
            
            return result["result"]
            
        except httpx.HTTPError as e:
            logger.error(f"런팟 서버 요청 실패: {e}")
            return input_text  # 실패 시 원본 텍스트 반환
        except Exception as e:
            logger.error(f"런팟 서버 응답 처리 실패: {e}")
            return input_text  # 실패 시 원본 텍스트 반환
    
    async def _refine_with_gpt(self, lora_output: str, original_text:str, user_profile: Dict, context: str) -> str:
        """ChatGPT로 2차 다듬기 (기존 OpenAIService 패턴 사용)"""
        if not self.services_available:
            return lora_output
        
        try:
            # 프롬프트엔지니어링_프롬프트 생성
            negative_preferences = user_profile.get('negativePreferences', {})
            prompts = self.prompt_engineer.generate_conversion_prompts(
                user_profile=user_profile,
                context=context,
                negative_preferences=negative_preferences
            )
            
            # 사용자 프로필에 따른 스타일 결정
            directness_level = user_profile.get('sessionDirectnessLevel', 
                                              user_profile.get('baseDirectnessLevel', 3))
            
            # 직설성 레벨에 따른 스타일 선택 
            if directness_level >= 4:
                style_key = 'direct'   
            elif directness_level <= 2:
                style_key = 'gentle'  
            else:
                style_key = 'neutral'

            refinement_prompt = f"""
다음은 공식 문서 변환 작업입니다.

【원본 텍스트】
{original_text}

【1차 LoRA 변환 결과】  
{lora_output}

【작업 지시사항】
{prompts.get(style_key, prompts.get('neutral', ''))}

위의 원본 텍스트와 1차 변환 결과를 참고하여, 원본의 의도를 유지하면서 1차 변환 결과를 더욱 자연스럽고 완성도 높은 공식 문서로 다듬어주세요.

- 원본 텍스트의 핵심 의미와 맥락을 보존
- 1차 변환의 공식적 톤을 유지하되 부자연스러운 부분 개선
- 누락된 정보가 있다면 원본을 참고하여 보완
"""

            
            refined_result = self.openai_service._convert_single_style(
                input_text=lora_output,
                prompt=refinement_prompt
            )
            
            return refined_result
            
        except Exception as e:
            logger.error(f"GPT 다듬기 실패: {e}")
            return lora_output
    
    async def convert_to_formal(self, 
                               input_text: str, 
                               user_profile: Dict, 
                               context: str = "business",
                               force_convert: bool = False) -> Dict:
        """
        공식 문서 변환 (런팟 추론 서버 + ChatGPT 파이프라인)
        
        Args:
            input_text: 변환할 텍스트
            user_profile: 사용자 프로필
            context: 컨텍스트 ("business", "report", "personal" 등)
            force_convert: 사용자가 명시적으로 "공식문서로 변환" 클릭한 경우 True
        """
        
        # 우선순위 1: 사용자 명시적 요청
        if force_convert:
            logger.info("사용자 명시적 요청으로 공식 문서 변환 강제 실행")
            should_convert = True
            conversion_reason = "user_explicit_request"
        else:
            # 우선순위 2: 자동 조건 판단
            should_convert = self._should_use_lora(user_profile, context)
            conversion_reason = "auto_condition" if should_convert else "condition_not_met"
        
        # 변환 조건에 해당하지 않는 경우
        if not should_convert:
            return {
                "success": False,
                "error": "공식 문서 변환 조건에 해당하지 않습니다.",
                "converted_text": "",
                "method": "none",
                "reason": conversion_reason
            }
        
        try:
            # 1차: 런팟 추론 서버 변환
            if self.is_inference_server_available:
                logger.info("런팟 추론 서버를 통한 1차 변환 시작")
                lora_output = await self._generate_with_lora(input_text)
                method = "lora_gpt"
            else:
                logger.warning("런팟 추론 서버 미사용, ChatGPT만 사용")
                lora_output = input_text
                method = "gpt_only"
            
            # 2차: ChatGPT 다듬기
            logger.info("ChatGPT를 통한 2차 다듬기 시작")
            final_output = await self._refine_with_gpt(
                lora_output = lora_output,
                original_text=input_text,
                user_profile=user_profile,
                context=context)
            
            return {
                "success": True,
                "converted_text": final_output,
                "lora_output": lora_output if self.is_inference_server_available else None,
                "method": method,
                "reason": conversion_reason,
                "forced": force_convert,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"공식 문서 변환 실패: {e}")
            return {
                "success": False,
                "error": f"변환 중 오류 발생: {str(e)}",
                "converted_text": "",
                "method": "error",
                "reason": conversion_reason
            }
    
    async def convert_by_user_request(self, 
                                     input_text: str, 
                                     user_profile: Dict, 
                                     context: str = "business") -> Dict:
        """사용자가 '공식문서로 변환' 버튼을 클릭했을 때 사용하는 메서드"""
        return await self.convert_to_formal(
            input_text=input_text,
            user_profile=user_profile,
            context=context,
            force_convert=True  # 항상 강제 변환
        )
    
    async def convert_to_business(
        self,
        input_text: str,
        user_profile: Dict
    ) -> Dict:
        """비즈니스 스타일로 변환 (버튼 클릭용)"""
        return await self.convert_by_user_request(input_text, user_profile, "business")

    async def convert_to_report(
        self,
        input_text: str,
        user_profile: Dict
    ) -> Dict:
        """보고서 스타일로 변환 (버튼 클릭용)"""
        return await self.convert_by_user_request(input_text, user_profile, "report")
    
    def get_status(self) -> Dict:
        """상태 정보"""
        return {
            "lora_status": "ready" if self.is_inference_server_available else "not_ready",
            "lora_model_path": "runpod_server",
            "services_available": self.services_available,
            "base_model_loaded": self.is_inference_server_available,
            "device": "runpod_gpu",
            "model_name": "gemma-2-2b-it",
            "inference_url": self.inference_url
        }