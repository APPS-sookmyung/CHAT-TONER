# python_backend/Dockerfile

FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

#--- [보안 강화] 일반 사용자 생성 ---
# 1. 'appuser'라는 이름의 새로운 사용자를 생성합니다.
#    --no-create-home: 홈 디렉토리를 만들지 않습니다.
#    --disabled-password: 비밀번호 로그인을 비활성화합니다.
RUN adduser --system --group --no-create-home appuser
# ------------------------------------

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 코드 복사
COPY . .

# --- [보안 강화] 파일 소유권 변경 및 사용자 전환 ---
# 2. /app 디렉토리와 그 안의 모든 파일의 소유권을 appuser에게 넘깁니다.
RUN chown -R appuser:appuser /app
# 3. 이후의 모든 명령을 appuser 권한으로 실행하도록 전환합니다.
USER appuser
# -------------------------------------------------

# 앱 실행
CMD ["uvicorn", "run_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
