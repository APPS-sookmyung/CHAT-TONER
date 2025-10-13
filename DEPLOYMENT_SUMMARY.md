# ChatToner Cloud Deployment Summary

## 배포 완료 상태 (2025-10-11)

### 배포된 서비스

#### 1. Backend (FastAPI)
- **URL**: https://chattoner-back-3yj2y7svbq-du.a.run.app
- **상태**: 배포 완료, 정상 작동
- **Region**: asia-northeast3
- **Image**: gcr.io/chattoner-project/chattoner-back:latest
- **Build Config**: `python_backend/cloudbuild.yaml`

**리소스 설정:**
- Memory: 2Gi
- CPU: 2
- Port: 8080 (자동 설정)
- Min instances: 0
- Max instances: 10
- Timeout: 300s

**환경 변수:**
```
ENVIRONMENT=production
DATABASE_URL=postgresql://chattoner-user:r~o+^[uD@6+p,kby@10.118.192.2:5432/chattoner
DB_HOST=10.118.192.2
DB_PORT=5432
DB_NAME=chattoner
DB_USER=chattoner-user
DB_PASS=r~o+^[uD@6+p,kby
```

**네트워크:**
- Cloud SQL: chattoner-project:asia-northeast3:chattoner
- VPC Connector: run-to-db-connector
- VPC Egress: private-ranges-only

**엔드포인트:**
- Health: `/api/v1/health`
- DB Health: `/api/v1/db-health`
- Docs: `/docs`
- All APIs: `/api/v1/*`

#### 2. Frontend (React + Nginx)
- **URL**: https://client-3yj2y7svbq-du.a.run.app
- **상태**: 배포 완료, 정상 작동
- **Region**: asia-northeast3
- **Image**: gcr.io/chattoner-project/chattoner-client:latest
- **Build Config**: `client/cloudbuild.yaml`

**리소스 설정:**
- Memory: 512Mi
- CPU: 1
- Port: 80
- Min instances: 0
- Max instances: 10

**Nginx 설정:**
- API Proxy: `/api/*` → Backend
- SPA Routing: 모든 경로를 index.html로
- Health Check: `/healthz` (설정됨, Cloud Run에서 차단됨)

### Cloud Build Triggers

#### 1. deploy-backend
- **ID**: 350f774a-9a95-4852-b8f4-798a3933593a
- **Description**: Deploy FastAPI backend when python_backend/ changes
- **Config File**: `python_backend/cloudbuild.yaml`
- **Repository**: APPS-sookmyung/CHAT-TONER (GitHub App)
- **Branch**: `^main$`
- **⚠️ TODO**: 포함된 파일 필터 추가 필요 → `python_backend/**`

#### 2. chattoner-client
- **ID**: 6dd0055b-6a26-4126-bd0f-bc729668c610
- **Description**: Deploy client to Cloud Run
- **Config File**: `cloudbuild.yaml` (root)
- **Repository**: APPS-sookmyung/CHAT-TONER (GitHub App)
- **Branch**: `^main$`
- **⚠️ TODO**: 포함된 파일 필터 추가 필요 → `client/**`

### 주요 이슈 및 해결사항

#### ✅ 해결된 문제

1. **PORT 환경 변수 충돌**
   - 문제: Cloud Run이 자동으로 PORT를 설정하는데 수동 설정 시도
   - 해결: `cloudbuild.yaml`에서 `PORT=8080` 제거

2. **잘못된 Docker 엔트리포인트**
   - 문제: `run_fastapi:app` 사용 (테스트용, API 라우터 없음)
   - 해결: `main:app`으로 변경 (전체 API 포함)

3. **SessionMiddleware import 오류**
   - 문제: `starlette.middleware.session` (오타)
   - 해결: `starlette.middleware.sessions`로 수정
   - 현재: 주석 처리됨 (필요시 활성화)

4. **VPC 및 Cloud SQL 설정 누락**
   - 문제: Cloud Run에서 Private IP DB 접근 불가
   - 해결: VPC connector, Cloud SQL instance 추가

5. **프론트엔드-백엔드 연결**
   - 문제: 프론트가 백엔드 API 호출 불가
   - 해결: nginx.conf에 `/api/*` 프록시 추가
   - Host 헤더: 백엔드 도메인으로 설정
   - SNI: `proxy_ssl_server_name on`

#### ⚠️ 진행 중인 문제

1. **DATABASE_URL 특수문자 이스케이프**
   - 문제: 비밀번호 `r~o+^[uD@6+p,kby`의 특수문자
   - URL 인코딩 필요: `r~o%2B%5E%5BuD%406%2Bp%2Ckby`
   - 현재: SQLite로 폴백됨
   - **다음 할 일**: URL 인코딩된 비밀번호로 DATABASE_URL 수정

2. **Cloud Build 트리거 파일 필터**
   - 문제: 모든 푸시에 모든 트리거 실행됨
   - **다음 할 일**: GCP 콘솔에서 필터 추가
     - `deploy-backend` → `python_backend/**`
     - `chattoner-client` → `client/**`

### 다음 작업 체크리스트

- [ ] DATABASE_URL 비밀번호 URL 인코딩 적용
  ```
  DATABASE_URL=postgresql://chattoner-user:r~o%2B%5E%5BuD%406%2Bp%2Ckby@10.118.192.2:5432/chattoner
  ```

- [ ] Cloud Build 트리거 파일 필터 추가 (GCP 콘솔):
  1. https://console.cloud.google.com/cloud-build/triggers/edit/350f774a-9a95-4852-b8f4-798a3933593a?project=chattoner-project
     - 포함된 파일 필터: `python_backend/**`
  2. https://console.cloud.google.com/cloud-build/triggers/edit/6dd0055b-6a26-4126-bd0f-bc729668c610?project=chattoner-project
     - 포함된 파일 필터: `client/**`

- [ ] OPENAI_API_KEY 설정 (선택사항)
  - Secret Manager 또는 환경 변수

- [ ] SessionMiddleware 활성화 (필요시)
  - `python_backend/main.py` 24, 86번 줄 주석 해제

### 파일 구조

```
2025-CHATTONER-Server/
├── python_backend/
│   ├── cloudbuild.yaml          # Backend CI/CD 설정
│   ├── Dockerfile                # Backend 컨테이너 이미지
│   ├── main.py                   # FastAPI 앱 엔트리포인트
│   ├── requirements.txt          # Python 의존성
│   └── database/
│       ├── db.py                 # DB 연결 (POSTGRES_URL 사용)
│       └── models.py             # DB 모델 (DATABASE_URL 환경변수 사용)
│
├── client/
│   ├── cloudbuild.yaml          # Client CI/CD 설정 (미사용, root 사용)
│   ├── Dockerfile                # Client 컨테이너 이미지
│   ├── nginx.conf                # Nginx 설정 (API 프록시)
│   └── src/
│       └── lib/api.ts            # API 클라이언트 (VITE_API_URL 사용)
│
├── cloudbuild.yaml               # Client CI/CD 설정 (실제 사용)
├── CLAUDE.md                     # Claude Code 가이드
├── DEPLOYMENT_INFO.md            # 배포 정보 (기존)
└── CLOUD_BUILD_SETUP.md          # Cloud Build 설정 가이드
```

### 참고 명령어

#### 수동 빌드 트리거
```bash
# Backend
gcloud builds triggers run deploy-backend --region=asia-northeast3 --branch=main

# Client (자동 트리거 안 될 때)
gcloud builds triggers run chattoner-client --region=asia-northeast3 --branch=main
```

#### 서비스 상태 확인
```bash
# 서비스 목록
gcloud run services list --region=asia-northeast3

# 서비스 상세
gcloud run services describe chattoner-back --region=asia-northeast3
gcloud run services describe client --region=asia-northeast3

# 로그 확인
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="chattoner-back"' --limit=20
```

#### 빌드 상태 확인
```bash
# 최근 빌드
gcloud builds list --region=asia-northeast3 --limit=5

# 특정 빌드 상세
gcloud builds describe <BUILD_ID> --region=asia-northeast3
```

### 현재 데이터베이스 상태

**⚠️ 주의**: 현재 SQLite를 사용 중 (`chat_toner.db`)
- `DATABASE_URL` 환경 변수가 제대로 설정되지 않음
- PostgreSQL 연결 문자열의 특수문자 이스케이프 필요

**데이터베이스 헬스 체크**:
```bash
curl https://chattoner-back-3yj2y7svbq-du.a.run.app/api/v1/db-health
```

현재 응답:
```json
{
  "connected": true,
  "dialect": "sqlite",
  "database": "./chat_toner.db",
  "tables": ["conversion_history", "negative_preferences", "rag_query_history", "user_profiles", "users", "vector_document_metadata"],
  "error": null
}
```

**목표 응답** (PostgreSQL 연결 후):
```json
{
  "connected": true,
  "dialect": "postgresql",
  "database": "chattoner",
  "tables": [...],
  "error": null
}
```

---

## 마지막 업데이트
- 날짜: 2025-10-11
- 작업자: Claude Code
- Git 커밋: eb9ad62 (fix: Add DATABASE_URL environment variable for PostgreSQL)
