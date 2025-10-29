from pydantic import BaseModel, Field
from typing import List, Literal

class CompanySurvey(BaseModel):
    """기업 설문조사 응답을 위한 Pydantic 모델"""
    company_name: str = Field(..., description="회사 이름")
    industry: str = Field(..., description="산업 분야") # Added field
    primary_business: str = Field(..., description="주요 사업 내용") # Added field
    team_size: int = Field(..., gt=0, description="팀 인원 수")
    communication_style: Literal['friendly', 'strict', 'formal'] = Field(..., description="주된 소통 성격")
    main_channel: List[str] = Field(..., description="주 소통 수단 (e.g., Slack, Email)") # Changed to List[str]
    main_target: List[str] = Field(..., description="주 커뮤니케이션 대상 (e.g., 내부 동료, 타부서, 경영진)")

    class Config:
        # 예시 데이터를 Swagger UI에 표시
        json_json_schema_extra = {
            "example": {
                "company_name": "ChatToner Corp",
                "industry": "IT", # Added example
                "primary_business": "Software Development", # Added example
                "team_size": 20,
                "communication_style": "friendly",
                "main_channel": ["Slack", "Email"], # Updated example
                "main_target": ["내부 동료", "타팀/타부서"]
            }
        }