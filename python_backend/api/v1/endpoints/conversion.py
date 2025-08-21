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

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from services.conversion_service import ConversionService
from ..schemas.conversion import ConversionRequest, ConversionResponse
from ..dependencies import get_conversion_service
import logging 

logger=logging.getLogger('chattoner')

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """간단한 테스트 엔드포인트"""
    print("[DEBUG] 테스트 엔드포인트 호출됨")
    return {"message": "테스트 성공", "status": "ok"}

@router.post("/convert")
async def convert_text(request: ConversionRequest, 
                      conversion_service: ConversionService = Depends(get_conversion_service)):
    """Text style conversion using actual AI service"""
    try:
        # Use the actual ConversionService with camelCase preservation
        user_profile_dict = request.user_profile.model_dump(by_alias=True, exclude_none=True)
        negative_preferences_dict = request.negative_preferences.model_dump(by_alias=True, exclude_none=True) if request.negative_preferences else None
        
        result = await conversion_service.convert_text(
            input_text=request.text,
            user_profile=user_profile_dict,
            context=request.context,
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
        import logging, traceback
        logger = logging.getLogger(__name__)
        logger.error("convert failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail="텍스트 변환 중 서버 오류가 발생했습니다.")

