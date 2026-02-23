#!/usr/bin/env python3
"""
FastAPI Swagger 및 OpenAPI 설정
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from typing import Dict, Any, Set, Type


try:
    # pydantic v2
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    BaseModel = object  # type: ignore

def configure_swagger(app: FastAPI) -> None:
    """Swagger 및 OpenAPI 설정"""

    TARGET_MODELS = {"DocumentIngestResponse", "OnboardingSurveyResponse"}

    def _fix_pydantic_examples_on_models() -> None:
        """
        get_openapi() 내부에서 OpenAPI(**output) 검증을 하기 전에,
        Pydantic v2 모델의 model_config['json_schema_extra']['examples']가 dict면
        list로 바꿔서 validation error를 막는다.
        """
        models: Set[Type[BaseModel]] = set()
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue

            # response_model
            rm = getattr(route, "response_model", None)
            if isinstance(rm, type) and issubclass(rm, BaseModel):
                models.add(rm)

            # request body model (있는 경우)
            body_field = getattr(route, "body_field", None)
            if body_field is not None:
                t = getattr(body_field, "type_", None)
                if isinstance(t, type) and issubclass(t, BaseModel):
                    models.add(t)

            # route 내부 response_field / response_fields에도 모델이 들어갈 수 있음
            response_field = getattr(route, "response_field", None)
            if response_field is not None:
                t = getattr(response_field, "type_", None)
                if isinstance(t, type) and issubclass(t, BaseModel):
                    models.add(t)

            response_fields = getattr(route, "response_fields", None)
            if isinstance(response_fields, dict):
                for f in response_fields.values():
                    t = getattr(f, "type_", None)
                    if isinstance(t, type) and issubclass(t, BaseModel):
                        models.add(t)
        for model in models:
            if getattr(model, "__name__", "") not in TARGET_MODELS:
                continue

            cfg = dict(getattr(model, "model_config", {}) or {})
            extra = dict(cfg.get("json_schema_extra") or {})

            if "examples" in extra and isinstance(extra["examples"], dict):
                ex = extra["examples"]

                # Case B: ExampleObject 단일 형태 {"summary": "...", "value": {...}} -> [dict]
                if any(k in ex for k in ("value", "summary", "description")):
                    extra["examples"] = [ex]
                else:
                    # Case A: {"success": {...}, "fail": {...}} -> values를 list로
                    extra["examples"] = list(ex.values())

                cfg["json_schema_extra"] = extra
                # 모델에 다시 반영
                setattr(model, "model_config", cfg)

    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        _fix_pydantic_examples_on_models()  

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

            ## Usage Flow
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
            {"name": "rag", "description": "RAG-based document search and intelligent Q&A"},
            {"name": "surveys", "description": "User survey and preferences collection"}
        ]

        # 보안 스키마는 주석 처리하여 문제를 피하자
        """
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