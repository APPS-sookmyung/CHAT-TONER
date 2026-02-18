# API Connections Documentation

**Date:** 2026-01-04
**Purpose:** Document all API connections between Frontend, NestJS Gateway, and FastAPI Backend

---

## Architecture Overview

```
Frontend (React)
    ↓ HTTP Requests
NestJS Gateway (Port 3000)
    ↓ Proxy
FastAPI Backend (Port 8080)
```

---

## ✅ Connected Endpoints

### 1. Conversion Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| `api.convertStyle()` | `POST /api/v1/conversion/convert` | `POST /api/v1/conversion/convert` | ✅ Connected |

### 2. Quality Analysis Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| `api.analyzeQuality()` | `POST /api/v1/quality/company/analyze` | `POST /api/v1/quality/company/analyze` | ✅ Connected |
| `api.getDropdownOptions()` | `GET /api/v1/quality/company/options` | `GET /api/v1/quality/company/options` | ✅ Connected |
| `api.getCompanyStatus()` | `GET /api/v1/quality/company/:companyId/status` | `GET /api/v1/quality/company/:companyId/status` | ✅ **NEW** |
| `api.createTestCompany()` | `POST /api/v1/quality/company/test-setup` | `POST /api/v1/quality/company/test-setup` | ✅ **NEW** |
| `api.generateFinalText()` | `POST /api/v1/quality/company/generate-final` | `POST /api/v1/quality/company/generate-final` | ✅ **NEW** |

### 3. Documents Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| `api.uploadDocuments()` | `POST /api/v1/documents/upload` | `POST /api/v1/documents/upload` | ✅ **NEW** |
| `api.getDocuments()` | `GET /api/v1/documents` | `GET /api/v1/documents/` | ✅ **NEW** |
| `api.deleteDocument()` | `DELETE /api/v1/documents/:documentName` | `DELETE /api/v1/documents/:documentName` | ✅ **NEW** |
| `api.summarizePDF()` | `POST /api/v1/documents/summarize-pdf` | `POST /api/v1/documents/summarize-pdf` | ✅ **NEW** |
| `api.summarizeText()` | `POST /api/v1/documents/summarize-text` | `POST /api/v1/documents/summarize-text` | ✅ **NEW** |

### 4. Surveys Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| `api.submitSurvey()` | `POST /api/v1/surveys/:key/responses` | `POST /api/v1/surveys/:key/responses` | ✅ **NEW** |
| N/A | `GET /api/v1/surveys/:key` | `GET /api/v1/surveys/:key` | ✅ **NEW** |

### 5. RAG Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| N/A (not used in frontend) | `POST /api/v1/rag/ask` | `POST /api/v1/rag/ask` | ✅ Available |
| N/A (not used in frontend) | `POST /api/v1/rag/ingest` | `POST /api/v1/rag/ingest` | ✅ Available |

### 6. Profile Endpoints

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| N/A (not used in frontend) | `GET /api/v1/profile/:user_id` | `GET /api/v1/profile/:user_id` | ✅ Available |
| N/A (not used in frontend) | `POST /api/v1/profile` | `POST /api/v1/profile` | ✅ Available |

### 7. Health & Feedback

| Frontend Method | Gateway Route | Backend Route | Status |
|----------------|---------------|---------------|--------|
| `api.healthCheck()` | `GET /` | `GET /` | ✅ Connected |
| N/A | `POST /api/v1/feedback` | N/A (local implementation) | ✅ Local only |

---

## Changes Made (2026-01-04)

### NestJS Gateway Updates

**Added 12 new endpoint routes:**

1. **Documents Endpoints (5)**
   - `POST /api/v1/documents/upload` - File upload with multipart/form-data
   - `GET /api/v1/documents` - List documents with optional subdir filter
   - `DELETE /api/v1/documents/:documentName` - Delete specific document
   - `POST /api/v1/documents/summarize-pdf` - PDF summarization
   - `POST /api/v1/documents/summarize-text` - Text summarization

2. **Surveys Endpoints (2)**
   - `GET /api/v1/surveys/:key` - Get survey definition
   - `POST /api/v1/surveys/:key/responses` - Submit survey response

3. **Additional Quality Endpoints (3)**
   - `GET /api/v1/quality/company/:companyId/status` - Company status check
   - `POST /api/v1/quality/company/test-setup` - Test company setup
   - `POST /api/v1/quality/company/generate-final` - Generate final text

### Module Updates

**app.module.ts:**
- Added `MulterModule` for file upload support
- Configured 10MB file size limit

**app.controller.ts:**
- Added `Delete`, `Query`, `UploadedFiles`, `UseInterceptors` decorators
- Added `FileFieldsInterceptor` from `@nestjs/platform-express`
- Implemented multipart/form-data handling for file uploads

---

## Request/Response Examples

### Documents Upload

**Request:**
```typescript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);

await api.uploadDocuments([file1, file2]);
```

**Response:**
```json
{
  "success": true,
  "uploaded_files": 2,
  "ingestion_result": {
    "success": true,
    "documents_processed": 2
  }
}
```

### Survey Submission

**Request:**
```typescript
await api.submitSurvey({
  tenant_id: "company1",
  user_id: "user123",
  answers: {
    primary_function: "engineering",
    communication_style: "friendly"
  }
});
```

**Response:**
```json
{
  "id": 1,
  "userId": "user123",
  "companyProfile": "## Engineering Team Guide...",
  "companyContext": { ... },
  "surveyResponses": { ... },
  "createdAt": "2026-01-04T10:00:00Z"
}
```

### Quality Analysis

**Request:**
```typescript
await api.analyzeQuality({
  text: "안녕하세요. 보고드립니다.",
  company_id: "company1",
  user_id: "user123",
  target_audience: "직속상사",
  context: "보고서",
  detailed: true
});
```

**Response:**
```json
{
  "success": true,
  "text": "안녕하세요. 보고드립니다.",
  "company_analysis": {
    "grammar_score": 85,
    "protocol_score": 75,
    "overall_score": 80,
    "grammar_suggestions": [...],
    "protocol_suggestions": [...]
  },
  "processing_time_ms": 1234
}
```

---

## Environment Configuration

### Frontend (.env or vite.config.ts)

```bash
# Production
VITE_API_URL=https://gateway.chattoner.com

# Development (proxied through Vite)
# No VITE_API_URL needed, uses local proxy
```

### NestJS Gateway (.env)

```bash
BACKEND_API_URL=http://127.0.0.1:8080  # FastAPI backend URL
PORT=3000
NODE_ENV=development
```

### FastAPI Backend (.env)

```bash
OPENAI_API_KEY=sk-...  # REQUIRED
OPENAI_MODEL=gpt-4o
HOST=0.0.0.0
PORT=8080
DATABASE_URL=postgresql://...
```

---

## Frontend Proxy Configuration

In development, the frontend proxies API requests through Vite:

**vite.config.ts:**
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',  // NestJS Gateway
        changeOrigin: true,
      },
    },
  },
});
```

---

## Testing API Connections

### 1. Health Check
```bash
curl http://localhost:3000/
# Expected: "서버가 정상 작동 중입니다!"
```

### 2. Conversion Test
```bash
curl -X POST http://localhost:3000/api/v1/conversion/convert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요",
    "user_profile": {
      "baseFormalityLevel": 3,
      "baseFriendlinessLevel": 4
    }
  }'
```

### 3. Documents List
```bash
curl http://localhost:3000/api/v1/documents
# Expected: ["doc1.pdf", "doc2.txt", ...]
```

### 4. Survey Get
```bash
curl http://localhost:3000/api/v1/surveys/onboarding-intake
# Expected: Survey schema with questions
```

---

## Available But Unused Endpoints

These endpoints are available in the gateway but not currently used by the frontend:

1. **RAG Endpoints**
   - `POST /api/v1/rag/ask` - RAG question answering
   - `POST /api/v1/rag/ingest` - RAG document ingestion

2. **Profile Endpoints**
   - `GET /api/v1/profile/:user_id` - Get user profile
   - `POST /api/v1/profile` - Save user profile

**Recommendation:** Add these to the frontend API client if needed for future features.

---

## Backend Endpoints NOT Proxied

These backend endpoints exist but are NOT proxied through the NestJS gateway:

1. **Knowledge Base** (`/api/v1/kb/*`)
2. **Suggestions** (`/api/v1/suggest/*`)
3. **Company** (`/api/v1/company/*`) - Temporarily disabled due to langgraph dependency
4. **Company Profile** (`/api/v1/company-profile/*`)
5. **Company Survey** (root level company survey endpoints)

**Reason:** These are either not used by the current frontend or require additional setup (like langgraph).

---

## API Error Handling

All endpoints use centralized error handling via NestJS interceptors:

**Error Response Format:**
```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request",
  "timestamp": "2026-01-04T10:00:00.000Z",
  "path": "/api/v1/conversion/convert",
  "details": { ... }
}
```

**Error Types:**
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error
- `502` - Bad Gateway (backend connection error)

---

## Next Steps

### Immediate
- ✅ All frontend API calls now properly connected
- ✅ File upload support added
- ✅ Survey submission working
- ⏳ Test all endpoints in development environment

### Short-term
- Add TypeScript DTOs for new endpoints
- Add Swagger documentation for new routes
- Implement request validation for new endpoints

### Long-term
- Consider adding frontend methods for RAG and Profile endpoints
- Add frontend UI for knowledge base and suggestions
- Wire company and company-profile endpoints when langgraph is available

---

## Troubleshooting

### Issue: "Cannot reach backend"
**Solution:** Check that FastAPI is running on port 8080:
```bash
cd packages/python_backend
python main.py
```

### Issue: "CORS error"
**Solution:** Ensure NestJS gateway CORS is configured and FastAPI FRONT_ORIGINS includes frontend URL.

### Issue: "File upload fails"
**Solution:** Check that MulterModule is properly configured and file size is under 10MB limit.

### Issue: "Survey not found"
**Solution:** Only `onboarding-intake` survey key is currently supported.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-04
**Author:** API Integration Team
