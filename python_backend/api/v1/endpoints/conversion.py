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
async def convert_text(request: ConversionRequest):
    """텍스트 스타일 변환"""
    print(f"[DEBUG] API 엔드포인트 진입")
    print(f"[DEBUG] 요청 데이터: {request}")
    try:
        print(f"[DEBUG] 변환 요청 받음: {request.text}")
        # 임시로 직접 서비스 생성
        from services.prompt_engineering import PromptEngineer
        from services.openai_services import OpenAIService
        from core.config import get_settings
        
        settings = get_settings()
        print(f"[DEBUG] OpenAI API Key 설정됨: {bool(settings.OPENAI_API_KEY)}")
        prompt_engineer = PromptEngineer()
        openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
        conversion_service = ConversionService(prompt_engineer, openai_service)
        print(f"[DEBUG] 서비스 생성 완료")
        
        result = await conversion_service.convert_text(
            input_text=request.text,
            user_profile=request.user_profile.model_dump(),
            context=request.context,
            negative_preferences=(
                request.negative_preferences.model_dump()
                if request.negative_preferences is not None else None
            )
        )
        
        return result
        
    # 내가 신경쓴 오류 체킹 
    except ValueError as e:
        print(f"[ERROR] 입력 값 오류: {e}")
        logger.warning(f"입력 값 오류: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        import traceback
        error_msg = f"변환 실패: {e}"
        traceback_msg = traceback.format_exc()
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback_msg}")
        logger.error(f"{error_msg}\nTraceback: {traceback_msg}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="텍스트 변환 중 서버 오류가 발생했습니다.") from e

