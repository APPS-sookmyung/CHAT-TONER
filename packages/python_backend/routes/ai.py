from fastapi import APIRouter, Body
from services.openai_services import OpenAIService

router = APIRouter()
ai_service = OpenAIService()

@router.post("/generate")
async def generate(prompt: str = Body(..., embed=True)):
    result = await ai_service.generate_text(prompt)
    return {"result": result}
