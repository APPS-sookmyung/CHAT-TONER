from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup for frontend integration (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 시 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic test endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI server is running normally"}

# Add actual API routers here
# from api.v1.routes import router as api_router
# app.include_router(api_router, prefix="/api/v1")
