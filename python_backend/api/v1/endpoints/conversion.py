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
    """Text style conversion"""
    try:
        original = request.text
        
        # Simple text conversion without mock prefixes
        return ConversionResponse(
            success=True,
            original_text=original,
            converted_texts={
                "direct": f"Direct: {original}",
                "gentle": f"Gentle: {original}",
                "neutral": f"Neutral: {original}"
            },
            context=request.context,
            metadata={"method": "simple"}
        )
        
    except Exception as e:
        print(f"[ERROR] 변환 중 오류: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"변환 중 오류 발생: {str(e)}")

