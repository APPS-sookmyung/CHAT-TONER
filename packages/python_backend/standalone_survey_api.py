#!/usr/bin/env python3
"""
독립형 설문 API 서버
벡터 스토어 의존성 없이 CompanyProfileService만 사용하는 최소한의 FastAPI 서버
"""

import asyncio
import uvicorn
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
import shutil

# 직접 import (의존성 주입 없이)
from services.company_profile_service import CompanyProfileService
from services.openai_services import OpenAIService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("standalone_survey")

app = FastAPI(
    title="Standalone Survey API",
    description="벡터 스토어 의존성 없는 독립형 설문 API",
    version="1.0.0"
)

class SurveySubmitRequest(BaseModel):
    tenant_id: str
    user_id: str
    answers: Dict[str, Any]

class SurveyResponse(BaseModel):
    id: int
    userId: str
    companyProfile: str
    companyContext: Dict[str, Any]
    surveyResponses: Dict[str, Any]
    createdAt: str
    message: Optional[str] = None
    profileType: str = "company_based"

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "standalone_survey_api"}

@app.get("/api/v1/surveys/{key}")
async def get_survey(key: str):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")
    return {
        "title": "온보딩 인테이크",
        "questions": [
            {"id": "primary_function", "type": "single_select", "label": {"ko": "주 업무 범주"}, "options": ["engineering", "sales", "operations", "hr", "finance"], "required": True},
            {"id": "communication_style", "type": "single_select", "label": {"ko": "소통 성격"}, "options": ["friendly", "formal", "strict", "casual"], "required": True},
            {"id": "team_size", "type": "single_select", "label": {"ko": "인원 수"}, "options": ["1-10", "11-50", "51-200", "201-1000", "1001+"], "required": True},
            {"id": "primary_channel", "type": "single_select", "label": {"ko": "주된 커뮤니케이션 채널"}, "options": ["email", "chat", "report", "meeting_minutes"], "required": True},
            {"id": "primary_audience", "type": "multi_select", "label": {"ko": "주 커뮤니케이션 대상"}, "options": ["peers_internal", "cross_team", "executives", "clients_vendors"], "required": True},
        ]
    }

@app.post("/api/v1/surveys/{key}/responses", response_model=SurveyResponse)
async def submit_survey(key: str, req: SurveySubmitRequest):
    if key != "onboarding-intake":
        raise HTTPException(404, "unknown survey key")

    logger.info(f"=== 독립형 설문 제출 시작 ===")
    logger.info(f"User ID: {req.user_id}")
    logger.info(f"Survey answers: {req.answers}")

    try:
        # CompanyProfileService 직접 사용 (의존성 주입 없이)
        logger.info("CompanyProfileService 직접 인스턴스 생성...")
        company_profile_service = CompanyProfileService()

        logger.info("generate_company_profile 호출 중...")
        profile_data = await company_profile_service.generate_company_profile(
            user_id=req.user_id,
            survey_answers=req.answers
        )
        logger.info(f"CompanyProfileService 성공! 데이터: {profile_data.keys()}")

        # 온보딩 완료 메시지 생성
        try:
            oai = OpenAIService()
            ob_msg = await oai.generate_text(
                f"팀 특성({profile_data['companyContext']['companySize']}, {profile_data['companyContext']['primaryFunction']})에 맞는 커뮤니케이션 가이드를 생성했습니다!",
                temperature=0.3,
                max_tokens=100,
            )
            logger.info(f"OnBoarding 메시지 생성 성공: {ob_msg}")
        except Exception as e:
            logger.warning(f"OnBoarding 메시지 생성 실패: {e}, 기본 메시지 사용")
            ob_msg = "팀 특성에 맞는 커뮤니케이션 가이드를 생성했습니다."

        response = SurveyResponse(
            id=profile_data["id"],
            userId=profile_data["userId"],
            companyProfile=profile_data["generatedProfile"],
            companyContext=profile_data["companyContext"],
            surveyResponses=profile_data["surveyResponses"],
            createdAt=profile_data["createdAt"],
            message=ob_msg,
            profileType=profile_data["profileType"]
        )

        logger.info("=== 독립형 설문 제출 완전 성공! ===")
        return response

    except Exception as e:
        logger.error(f"=== 독립형 설문 처리 실패 ===")
        logger.error(f"오류: {e}")
        logger.error(f"오류 타입: {type(e)}")
        logger.error("스택 트레이스:", exc_info=True)

        # 기본 폴백 응답
        fallback_context = {
            "companySize": "일반 조직",
            "teamSize": req.answers.get("team_size", "알 수 없음"),
            "primaryFunction": req.answers.get("primary_function", "일반"),
            "communicationStyle": req.answers.get("communication_style", "친근함"),
            "primaryChannel": req.answers.get("primary_channel", "이메일"),
            "primaryAudience": req.answers.get("primary_audience", []),
            "sizeCharacteristics": ["효율적 소통"],
            "functionCharacteristics": ["전문성", "협업"]
        }

        fallback_profile = f"""
## {fallback_context['companySize']} 커뮤니케이션 가이드

### 핵심 원칙
1. **명확성**: 목적과 기대사항을 구체적으로 전달
2. **효율성**: 체계적이고 간결한 소통
3. **협업**: 팀워크를 고려한 건설적인 대화

실무에서 상황에 맞게 조정하여 사용하세요.
"""

        return SurveyResponse(
            id=999,
            userId=req.user_id,
            companyProfile=fallback_profile,
            companyContext=fallback_context,
            surveyResponses=req.answers,
            createdAt=datetime.now().isoformat(),
            message="기본 커뮤니케이션 가이드를 생성했습니다.",
            profileType="company_based"
        )

# 문서 업로드 및 관리 API
UPLOAD_DIR = "database/documents"

def ensure_upload_dir():
    """업로드 디렉토리 생성"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """문서 업로드 API"""
    ensure_upload_dir()

    uploaded_files = []
    try:
        for file in files:
            if not file.filename:
                continue

            # 파일 확장자 확인
            allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(400, f"지원하지 않는 파일 형식: {file_extension}")

            # 파일 저장
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded_files.append(file.filename)
            logger.info(f"파일 업로드 완료: {file.filename}")

        return {
            "message": f"{len(uploaded_files)}개 파일이 업로드되었습니다.",
            "files": uploaded_files
        }

    except Exception as e:
        logger.error(f"파일 업로드 실패: {e}")
        raise HTTPException(500, f"파일 업로드 실패: {str(e)}")

@app.get("/api/v1/documents/")
async def get_documents(subdir: str = None):
    """문서 목록 조회 API"""
    ensure_upload_dir()

    try:
        target_dir = UPLOAD_DIR
        if subdir:
            target_dir = os.path.join(UPLOAD_DIR, subdir)

        if not os.path.exists(target_dir):
            return []

        documents = []
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            if os.path.isfile(file_path):
                documents.append(filename)

        documents.sort()
        logger.info(f"문서 목록 조회: {len(documents)}개 파일")
        return documents

    except Exception as e:
        logger.error(f"문서 목록 조회 실패: {e}")
        raise HTTPException(500, f"문서 목록 조회 실패: {str(e)}")

@app.delete("/api/v1/documents/{document_name}")
async def delete_document(document_name: str):
    """문서 삭제 API"""
    ensure_upload_dir()

    try:
        file_path = os.path.join(UPLOAD_DIR, document_name)

        if not os.path.exists(file_path):
            raise HTTPException(404, f"파일을 찾을 수 없습니다: {document_name}")

        os.remove(file_path)
        logger.info(f"파일 삭제 완료: {document_name}")

        return {"message": f"파일이 삭제되었습니다: {document_name}"}

    except FileNotFoundError:
        raise HTTPException(404, f"파일을 찾을 수 없습니다: {document_name}")
    except Exception as e:
        logger.error(f"파일 삭제 실패: {e}")
        raise HTTPException(500, f"파일 삭제 실패: {str(e)}")

# 회사 프로필 조회 API
@app.get("/api/v1/company-profile/{user_id}")
async def get_company_profile(user_id: str):
    """사용자의 회사 프로필 조회 API"""
    try:
        company_profile_service = CompanyProfileService()
        profile = company_profile_service.get_profile(user_id)

        if not profile:
            raise HTTPException(404, f"사용자 '{user_id}'의 프로필을 찾을 수 없습니다.")

        logger.info(f"회사 프로필 조회 성공: {user_id}")
        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회사 프로필 조회 실패: {e}")
        raise HTTPException(500, f"프로필 조회 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("=== 독립형 설문 API 서버 시작 ===")
    print("벡터 스토어 의존성 없이 CompanyProfileService만 사용")
    print("포트: 6000")

    uvicorn.run(app, host="0.0.0.0", port=6002, log_level="info")