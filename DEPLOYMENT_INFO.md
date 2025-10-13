# ChatToner 배포 환경 정보

## 프로젝트 정보
- **Project ID**: `chattoner-project`
- **GitHub Repository**: `APPS-sookmyung/CHAT-TONER`
- **Region**: `asia-northeast3` (Seoul)

---

## Cloud Run 서비스

### 1. Backend (Python FastAPI)
- **Service Name**: `chattoner-back`
- **Image**: `gcr.io/chattoner-project/chattoner-back:latest`
- **Port**: 8080
- **Memory**: 2Gi
- **CPU**: 2
- **Secrets**:
  - `DATABASE_URL` (from Secret Manager)
  - `OPENAI_API_KEY` (from Secret Manager)

### 2. Client (Frontend)
- **Service Name**: `client`
- **Image**: `gcr.io/chattoner-project/chattoner-client:latest`
- **Port**: 80
- **Memory**: 512Mi
- **CPU**: 1

---

## Cloud Build 설정

### Backend 트리거
```
이름: deploy-backend
이벤트: Push to branch
브랜치: ^main$
구성 파일: python_backend/cloudbuild.yaml
포함된 파일: python_backend/**,requirements.txt
```

### Client 트리거 (예정)
```
이름: deploy-client
이벤트: Push to branch
브랜치: ^main$
구성 파일: client/cloudbuild.yaml
포함된 파일: client/**
```

---

## CI/CD 워크플로우

1. **코드 수정 후 GitHub에 푸시**
   - `python_backend/` 수정 → `chattoner-back` 자동 배포
   - `client/` 수정 → `client` 자동 배포

2. **빌드 프로세스**
   - Docker 이미지 빌드
   - GCR에 이미지 푸시 (latest + commit SHA 태그)
   - Cloud Run에 자동 배포

3. **배포 완료**
   - Cloud Run이 자동으로 새 버전 배포
   - 무중단 배포 (zero downtime)

---

## 필수 Secret Manager 항목

```bash
# Backend용 시크릿
gcloud secrets create DATABASE_URL --project=chattoner-project
gcloud secrets create OPENAI_API_KEY --project=chattoner-project
```

---

## 현재 상태 (2025-10-04)

### ✅ 완료
- [x] `python_backend/cloudbuild.yaml` 생성 및 main 브랜치 푸시
- [x] 서비스 이름을 기존 환경에 맞게 수정 (`chattoner-back`, `client`)
- [x] Cloud Build 권한 설정 완료

### ⏳ 진행 중
- [ ] `deploy-backend` 트리거 생성
- [ ] Secret Manager에 DATABASE_URL, OPENAI_API_KEY 등록
- [ ] 백엔드 자동 배포 테스트

### 📋 예정
- [ ] `client/cloudbuild.yaml` main 브랜치 푸시
- [ ] `deploy-client` 트리거 생성
- [ ] 프론트엔드 자동 배포 테스트
- [ ] `database/cloudbuild.yaml` 수동 트리거 설정 (DB 마이그레이션용)

---

## 트러블슈팅

### 빌드 실패 시
1. Cloud Build 로그 확인: https://console.cloud.google.com/cloud-build/builds?project=chattoner-project
2. Secret Manager 시크릿 존재 여부 확인
3. 권한 확인 (Cloud Build 서비스 계정)

### 배포 실패 시
1. Cloud Run 로그 확인: https://console.cloud.google.com/run?project=chattoner-project
2. 환경 변수 및 시크릿 설정 확인
3. Dockerfile 및 애플리케이션 포트 확인

---

## 유용한 명령어

### 서비스 URL 확인
```bash
gcloud run services describe chattoner-back --region=asia-northeast3 --project=chattoner-project --format="value(status.url)"
gcloud run services describe client --region=asia-northeast3 --project=chattoner-project --format="value(status.url)"
```

### 수동 빌드/배포
```bash
# Backend
gcloud builds submit --config=python_backend/cloudbuild.yaml python_backend/ --project=chattoner-project

# Client
gcloud builds submit --config=client/cloudbuild.yaml client/ --project=chattoner-project
```

### 빌드 히스토리 확인
```bash
gcloud builds list --limit=10 --project=chattoner-project
```

### 로그 확인
```bash
# 특정 빌드 로그
gcloud builds log BUILD_ID --project=chattoner-project

# Cloud Run 로그
gcloud run services logs read chattoner-back --region=asia-northeast3 --project=chattoner-project
```
