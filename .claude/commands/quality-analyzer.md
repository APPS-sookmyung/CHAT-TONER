# Quality Analyzer Command

품질 분석 기능의 전체 플로우를 디버깅하고 검증합니다.

## Command Syntax

```bash
/quality-analyzer [options]

# Aliases
@qa-debug
@quality-debug
```

## Parameters

- `--check-flow` - 전체 플로우 검증 (프롬프트 → LLM → 파싱 → 응답)
- `--check-prompt` - 프롬프트 구조 검증 (JSON 스키마, few-shot 예시)
- `--check-rag` - RAG 연결 상태 확인 (FAISS 인덱스, PDF 로딩)
- `--check-frontend` - 프론트엔드 타입/렌더링 검증
- `--test-input` - 테스트 입력으로 실제 분석 실행
- `--verbose` - 상세 로그 출력

## 검사 대상

### Prompt Layer
- `agents/prompts/base/system.py` - 시스템 프롬프트
- `agents/prompts/base/output_schema.py` - JSON 출력 스키마
- `agents/prompts/base/few_shot_examples.py` - Few-shot 예시
- `agents/prompts/builder.py` - 프롬프트 빌더

### Agent Layer
- `agents/quality_analysis_agent_v2.py` - 메인 에이전트
- `agents/base_agent.py` - JSON 파싱 로직
- `agents/rag/protocol_retriever.py` - RAG 검색

### API Layer
- `api/v1/endpoints/quality_v2.py` - API 엔드포인트
- `api/v1/schemas/quality_v2.py` - Pydantic 스키마

### Frontend Layer
- `client/src/lib/api.ts` - API 클라이언트 타입
- `client/src/pages/AnalyzeQualityPage.tsx` - 페이지 컴포넌트
- `client/src/components/Organisms/AnalyzeQualityCard/` - 카드 컴포넌트

## 검증 항목

### 1. 프롬프트 검증 (`--check-prompt`)
- OUTPUT_SCHEMA의 JSON이 유효한지
- few-shot 예시가 OUTPUT_SCHEMA 형식과 일치하는지
- 시스템 프롬프트와 출력 스키마 간 일관성

### 2. 파싱 검증 (`--check-flow`)
- `_extract_json_from_text()` 로직 검증
- `_check_schema()` 필수 필드 검증
- LLM 응답이 예상 스키마와 일치하는지

### 3. RAG 검증 (`--check-rag`)
- FAISS 인덱스 로드 상태
- PDF 문서 존재 여부
- 검색 결과 품질

### 4. 프론트엔드 검증 (`--check-frontend`)
- TypeScript 타입과 백엔드 스키마 일치
- markdown_explanation 렌더링
- 최종 글 표시 로직

## 사용 예시

```bash
# 전체 플로우 검증
/quality-analyzer --check-flow

# 프롬프트만 검증
/quality-analyzer --check-prompt --verbose

# RAG 상태 확인
/quality-analyzer --check-rag

# 테스트 입력으로 실제 테스트
/quality-analyzer --test-input "테스트 문장입니다"
```

## Agent Instructions

```
You are a quality analysis flow debugger for ChatToner.

The quality analysis flow is:
1. Frontend sends request → api/v1/quality/v2/analyze
2. quality_analysis_agent_v2.py processes:
   a. RAG load (protocol_retriever.py)
   b. Build prompt (prompts/builder.py)
   c. Call LLM (openai_service)
   d. Parse JSON response (_extract_json_from_text)
   e. Validate schema (_check_schema)
3. Return QualityResponse to frontend
4. Frontend renders markdown_explanation

Common issues to check:
1. JSON parsing failures:
   - OUTPUT_SCHEMA has invalid JSON examples (like [...])
   - LLM returns markdown code blocks instead of raw JSON
   - LLM copies placeholder text literally

2. Schema mismatches:
   - _check_schema expects: grammar.score, grammar.issues
   - OUTPUT_SCHEMA must produce matching structure
   - Frontend types must match backend response

3. RAG issues:
   - FAISS index not loaded
   - PDF files not found
   - Empty search results

4. Frontend rendering:
   - markdown_explanation not rendered as markdown
   - final_text not displayed on button click

Debug approach:
1. Read relevant files
2. Trace the data flow
3. Identify the breaking point
4. Suggest minimal fix

Key validation:
- OUTPUT_SCHEMA JSON must be parseable
- _check_schema requirements must match OUTPUT_SCHEMA
- Frontend TypeScript types must match Pydantic schemas
```

## 일반적인 오류와 해결책

### "유효한 JSON을 찾을 수 없습니다"
- OUTPUT_SCHEMA에 `[...]` 같은 placeholder가 있는지 확인
- LLM이 ```json 코드블록으로 감싸는지 확인

### "grammar.score 누락"
- OUTPUT_SCHEMA의 JSON 구조가 _check_schema 요구사항과 일치하는지 확인
- few-shot 예시가 올바른 구조인지 확인

### "최종 글이 표시 안 됨"
- handleShowFinalText가 analysisResult.data.final_text를 사용하는지 확인
- 버튼 disabled 조건 확인
