# ChatToner

**개인화 톤 변환 시스템**  
Chat-toner는 상황과 대상에 맞는 말투 스타일을 개인화하여 변환해주는 서비스입니다.  
사용자 피드백을 기반으로 지속적으로 코칭과 추천이 정교화됩니다.

---

## 📝 프로젝트 개요 (Project Overview)

Chat-toner는 단순한 어투 변환을 넘어, 대화 목적/상황/대상별 맞춤 스타일을 추천하고  
사용자 고유의 말투 특성을 학습해 점진적으로 고도화되는 개인화 스타일 변환 시스템입니다.

---

## 🚀 주요 기능 (Key Features)

- **상황별 톤 제안**
  - 업무, 친구, 공식 등 다양한 상황에 맞는 톤 자동 제시
- **대상 및 목적 기반 스타일 추천**
- **문장 변환 & 실시간 피드백**
  - 한 문장을 여러 스타일로 변환, 선택 옵션 제공
  - 실시간 피드백/수정 UI 제공
- **개인화 습관 학습**
  - LoRA 기반 사용자 어투 모델링
  - 사용자의 선택/피드백을 통한 지속적 개인화

---

## 🛠️ 기술 스택 (Tech Stack)

| 분류         | 스택/라이브러리                                 | 용도                              |
| :----------- | :---------------------------------------------- | :-------------------------------- |
| **Frontend** | React.js, TypeScript, Zustand                   | 인터페이스, 타입 안정성, 상태관리 |
| **Backend**  | Flask, FastAPI, Express.js                      | ML API, 프록시, 정적 파일         |
| **ML**       | LoRA, KoGPT, KoAlpaca, HuggingFace Transformers | 스타일 변환, 텍스트 생성          |
| **Database** | PostgreSQL, FAISS, Redis                        | 데이터 저장, 벡터 검색, 캐싱      |

---

## 🗂️ 프로젝트 구조 (Project Structure)

chattoner/
├── client/
│ └── ... (React 프론트엔드)
├── server/
│ └── ... (Express 프록시)
├── python_backend/
│ ├── app/
│ ├── ml/
│ └── requirements.txt
├── docker-compose.yml
└── README.md

text

---

## ⚡ 설치 및 실행 (Installation & Setup)

1. **프로젝트 클론**

   ```
   git clone https://github.com/your-username/chat-toner.git
   cd chat-toner
   ```

2. **환경 구성**

   ```
   npm install              # Node.js
   cd client && npm install # 클라이언트
   cd ../python_backend && pip install -r requirements.txt
   ```

3. **DB 및 환경 변수**

   ```
   createdb chattoner
   cp .env.example .env
   # .env에서 DB 연결 정보 수정
   ```

4. **실행**
   ```
   npm run dev          # Dev 전체 실행
   # 또는
   npm run client       # React
   npm run server       # Express
   npm run python       # Flask
   ```

---

## 💡 사용 방법 (Usage)

- 텍스트 입력 → 상황 선택(업무/친구/공식) → 변환 옵션 선택 → 결과 피드백 제공

---

## 📈 개발 전략 (Development Strategy)

- **MVP**: 프롬프트 기반 기본 기능 우선
- **모델 개발**: LoRA 활용 개인화 고도화
- **통합**: RAG, 벡터 검색 최적화
- **성능/UX 최적화**

---

## 🧪 평가 방법

- 결과 적절성 수동 평가, 사용자 O/X 만족도 조사
- 다양한 알고리즘(A/B) 성능 비교

---

## 🤝 기여하기 (Contributing)

1. Fork this repo
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit (`git commit -m 'Add ...'`)
4. Push (`git push origin feature/NewFeature`)
5. Pull Request 제출

---

## 👥 팀원 소개 (Team)

| 이름       | 역할        | 담당 내용                 | 연락처                |
| :--------- | :---------- | :------------------------ | :-------------------- |
| **윤지원** | PM          | 프로젝트 기획, 총괄       | geenieeyoon@gmail.com |
| **권유진** | Development | 풀스택, ML 모델 개발 지원 | apps@email.com        |
| **연구진** | Research    | ML 모듈/개인화 연구/개발  | apps@email.com        |

> **APPS (앱/웹 개발 학회)**  
> 이 프로젝트는 소프트웨어학부 APPS 학회가 수행하는 연구 프로젝트입니다.

---

## 📫 연락처 (Contact)

- Email: [앱스 학회 이메일]
- GitHub: [Organization GitHub]
- Notion: [프로젝트 노션 페이지]

---

# Repository Guidelines

## Project Structure & Module Organization

- Source lives in `src/`; tests in `tests/`; configs in `configs/`; scripts in `scripts/`. Common extras: `Dockerfile`, `.env.example`, `docs/`.
- Typical entrypoints: Node `src/index.ts` or `src/server.ts`; Python `src/main.py` or `app/main.py`.
- Organize features under `src/<feature>/` (e.g., `src/auth/`, `src/chat/`) with small, focused modules.

## Build, Test, and Development Commands

- Node.js
  - `npm ci` — install exact deps. `npm run dev` — start in watch mode.
  - `npm test` — run unit tests. `npm run build` — produce production build.
  - `npm run lint` / `npm run format` — check/auto-fix style.
- Python
  - `python -m venv .venv && . .venv/bin/activate` then `pip install -r requirements.txt`.
  - `pytest` — run tests. `ruff check .` and `black .` — lint/format.
  - `uvicorn app.main:app --reload` or `python -m src.main` — run locally.
- Docker
  - `docker compose up --build` — run full stack with services.

## Coding Style & Naming Conventions

- TypeScript/JS: 2-space indent, `camelCase` for vars, `PascalCase` for classes, file names `kebab-case.ts`.
- Python: 4-space indent, `snake_case` for vars, `PascalCase` for classes, file names `snake_case.py`.
- Keep functions focused (<50 LOC), prefer pure utils, validate inputs at boundaries.
- Use linters/formatters configured in the repo (e.g., ESLint+Prettier or Ruff+Black) before committing.

## Testing Guidelines

- Mirror structure: `tests/<feature>/` matches `src/<feature>/`.
- Name tests `*.spec.ts`/`*.test.ts` (Node) or `test_*.py` (Python).
- Target ≥80% line coverage; include happy-path and edge cases. Run with `npm test -- --coverage` or `pytest --cov`.

## Commit & Pull Request Guidelines

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`.
- PRs include: concise description, linked issues (e.g., `Closes #123`), local test steps, and API examples (e.g., `curl` sample) or screenshots when UI-related.
- Keep PRs small and focused; update docs and `.env.example` when config changes.

## Security & Configuration Tips

- Never commit secrets. Copy `.env.example` to `.env` and adjust locally.
- Restrict CORS, validate all inputs, avoid logging PII, and run `npm audit` or `pip-audit` regularly.
- Review Docker base images and pin critical versions.

## Agent-Specific Notes

- If unsure of stack, check `package.json` (Node) or `pyproject.toml/requirements.txt` (Python) and follow matching commands above.
- Follow this AGENTS.md across the repo; prefer minimal, targeted changes with matching tests.
