"""텍스트 변환 API 엔드포인트
신경 쓴 점: 
- 라우터 분리 + DI 구성 
- 의존성 주입 -> Depends + Provide 사용

신경 써야 하는점: 
1. 피드백 route 에 요청/응답 모델 정의
2. exception 처리 개선 
3. 공통 응답 메세지는 모델로 정의 
4. 의미 있는 status code 분리 
5. pydantic 모델이 request body 에서 명시적임을 보장 
"""

from fastapi import APIRouter, Depends, HTTPException
import logging 
import traceback
from typing import Optional, Dict, Any

from services.conversion_service import ConversionService
from ..schemas.conversion import ConversionRequest, ConversionResponse
from ..dependencies import get_conversion_service

from api.v1.dependencies import get_user_preferences_service
from services.user_preferences import UserPreferencesService

logger=logging.getLogger('chattoner')
router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """간단한 테스트 엔드포인트"""
    logger.debug("테스트 엔드포인트 호출됨")
    return {"message": "테스트 성공", "status": "ok"}

def clamp_1_10(x, default=5) -> int:
    try:
        v = int(x)
    except Exception:
        v = default
    return max(1, min(10, v))

@router.post("/convert")
async def convert_text(
    request: ConversionRequest,
    conversion_service: ConversionService = Depends(get_conversion_service),
    user_service: UserPreferencesService = Depends(get_user_preferences_service),
):
    """Text style conversion using actual AI service"""
    user_profile_dict = {
        "baseFormalityLevel": 5,
        "baseFriendlinessLevel": 5,
        "baseEmotionLevel": 5,
        "baseDirectnessLevel": 5,
    }
    company_profile_text = None
    company_context = None
    
    try:

        if getattr(request, "user_profile", None) is not None:
            user_profile_dict.update (
                request.user_profile.model_dump(by_alias=True, exclude_none=True)
            )
        elif getattr(request, "userId", None):
            profile_data = user_service.get_user_profile(request.userId)

            if not profile_data:
                logger.warning("No profile found for userId=%s. Using defaults.", request.userId)
            else:
                company_profile_text = profile_data.get("companyProfile") or profile_data.get("message")
                company_context = profile_data.get("companyContext")

                maybe_levels = profile_data.get("user_profile") or profile_data.get("userProfile")
                if isinstance(maybe_levels, dict):
                    user_profile_dict.update(maybe_levels)

        user_profile_dict["baseFormalityLevel"] = clamp_1_10(user_profile_dict.get("baseFormalityLevel"))
        user_profile_dict["baseFriendlinessLevel"] = clamp_1_10(user_profile_dict.get("baseFriendlinessLevel"))
        user_profile_dict["baseEmotionLevel"] = clamp_1_10(user_profile_dict.get("baseEmotionLevel"))
        user_profile_dict["baseDirectnessLevel"] = clamp_1_10(user_profile_dict.get("baseDirectnessLevel"))

        negative_preferences_dict = (
            request.negative_preferences.model_dump(by_alias=True, exclude_none=True)
            if getattr(request, "negative_preferences", None)
            else None
        )

        effective_context = request.context

        instruction_parts = []
        if company_profile_text:
            instruction_parts.append(f"[회사 커뮤니케이션 가이드]\n{company_profile_text}")
        if company_context:
            instruction_parts.append(f"[회사 컨텍스트]\n{company_context}")

        if instruction_parts:
            effective_context = (
                f"{request.context}\n\n"
                "[지침] 아래 정보를 참고하되, 반드시 '원본 텍스트'를 변환하세요. "
                "가이드 문장을 그대로 출력하지 마세요.\n\n"
                + "\n\n".join(instruction_parts)
            )

        logger.info("input_text=%r", request.text)
        logger.info("context_prefix=%r", effective_context[:200] if effective_context else None)
        logger.info("user_profile_dict=%s", user_profile_dict)

        result = await conversion_service.convert_text(
            input_text=request.text,
            user_profile=user_profile_dict,
            context=effective_context,
            negative_preferences=negative_preferences_dict
        )

        return ConversionResponse(
            success=result.get("success", True),
            original_text=request.text,
            converted_texts=result.get("converted_texts", {}),
            context=request.context,
            sentiment_analysis=result.get("sentiment_analysis"),
            metadata=result.get("metadata", {})
        )

    except Exception as e:
        logger.error("convert failed: %s\n%s", e, traceback.format_exc())

        # FALLBACK: Direct LLM call when conversion service fails
        try:
            from services.openai_services import OpenAIService
            oai = OpenAIService()

            formality = clamp_1_10(user_profile_dict.get("baseFormalityLevel"), default=5)
            friendliness = clamp_1_10(user_profile_dict.get("baseFriendlinessLevel"), default=5)
            emotion = clamp_1_10(user_profile_dict.get("baseEmotionLevel"), default=5)
            directness = clamp_1_10(user_profile_dict.get("baseDirectnessLevel"), default=5)

            fallback_prompt = f"""
다음 한국어 텍스트를 아래 스타일로 변환해주세요.

- 격식도: {formality}/10
- 친근함: {friendliness}/10
- 감정표현: {emotion}/10
- 직설성: {directness}/10

상황: {request.context}

원본 텍스트:
{request.text}

변환된 텍스트만 반환하세요.
""".strip()

            converted = await oai.generate_text(
                fallback_prompt, temperature=0.3, max_tokens=300
            )

            return ConversionResponse(
                success=True,
                original_text=request.text,
                converted_texts={"converted": converted.strip()},
                context=request.context,
                sentiment_analysis={"fallback": True},
                metadata={"method": "llm-fallback", "reason": "service-error"},
            )

        except Exception as fallback_error:
            logger.error("Fallback also failed: %s\n%s", fallback_error, traceback.format_exc())
            raise HTTPException(status_code=500, detail="텍스트 변환 중 서버 오류가 발생했습니다.")