#!/usr/bin/env python3
"""
FastAPI Swa        schema[\"tags\"] = [
            {\"name\": \"health\", \"description\": \"Server status and connection check\"},
            {\"name\": \"conversion\", \"description\": \"AI-based text style conversion (core feature)\"},
            {\"name\": \"profile\", \"description\": \"User personalization profile management\"},
            {\"name\": \"quality\", \"description\": \"Text quality analysis (grammar/readability/formality)\"},
            {\"name\": \"enterprise\", \"description\": \"Corporate style analysis and conversion services\"},
            {\"name\": \"rag\", \"description\": \"RAG-based document search and intelligent Q&A\"},
        ]및 OpenAPI 설정
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def configure_swagger(app: FastAPI) -> None:
    """Swagger 및 OpenAPI 설정"""

    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        
        schema = get_openapi(
            title="ChatToner API",
            version="1.0.0",
            description="""
            **ChatToner** - AI-based Korean text personalization service
            
            ## Main Features
            - **텍스트 스타일 변환**: 사용자 맞춤 톤 변환 (격식/친근/중립)
            - **품질 분석**: 문법, 가독성, 격식성 자동 점검
            - **RAG 시스템**: 문서 기반 스타일 가이드 검색
            - **개인화**: 사용자 피드백 학습 및 프로필 적응
            
            ## 🛠 사용 흐름
            1. `/api/v1/conversion/convert` - 텍스트 변환 요청
            2. `/api/v1/quality/analyze` - 품질 점수 확인  
            3. `/api/v1/feedback` - 피드백 제출
            4. `/api/v1/rag/ask` - 스타일 가이드 질의응답
            """,
            routes=app.routes,
        )

        schema["tags"] = [
            {"name": "health", "description": "Server status and connection check"},
            {"name": "conversion", "description": "AI-based text style conversion (core feature)"},
            {"name": "profile", "description": "User personalization profile management"},
            {"name": "quality", "description": "Text quality analysis (grammar/readability/formality)"},
            {"name": "enterprise", "description": "Corporate style analysis and conversion services"},
            {"name": "rag", "description": "RAG-based document search and intelligent Q&A"}
        ]
        """
        # 보안 스키마 
        schema["components"] = schema.get("components", {})
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }

        for path_data in schema["paths"].values():
            for operation in path_data.values():
                if "security" not in operation:
                    operation["security"] = [{"BearerAuth": []}]
        
        """
        
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

def get_swagger_ui_parameters() -> Dict[str, Any]:
    """Swagger UI 커스터마이징 파라미터"""
    return {
        "swagger_ui_parameters": {
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "operationsSorter": "method",
            "filter": True,
            "tagsSorter": "alpha",
            "tryItOutEnabled": True,
            "layout": "BaseLayout",
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "showExtensions": True,
            "showCommonExtensions": True,
        }
    }