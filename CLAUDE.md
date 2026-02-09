# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chat-Toner is an AI-powered communication assistant that helps users adjust tone and style in their writing. It's built on a microservices architecture with three main components:

1. **React Frontend** (`packages/client/`) - Vite-based React app with TypeScript and TanStack Query
2. **NestJS API Gateway** (`packages/nestjs-gateway/`) - Proxies requests to the Python backend
3. **FastAPI Backend** (`packages/python_backend/`) - Core AI/ML logic using LangChain, OpenAI, and RAG

## Common Commands

### Root-level commands (run from project root):

```bash
# Install all dependencies across workspaces
npm install

# Build all packages
npm run build

# Type checking
npm run check                    # Check all packages
npm run check:gateway            # Check NestJS gateway only
npm run check:client             # Check client only

# Run individual services in development
npm run dev:client               # Start React frontend (port 5173)
npm run dev:gateway              # Start NestJS gateway (port 3000)
npm run dev:python               # Start Python FastAPI backend (port 8080)

# Database operations (uses Drizzle)
npm run db:push                  # Push schema changes to database
```

### Python Backend (packages/python_backend/):

```bash
cd packages/python_backend

# Run the FastAPI server
python main.py

# Run tests
pytest                           # Run all tests with coverage
pytest tests/test_rag_endpoints.py  # Run specific test file
pytest -m "not slow"             # Skip slow tests
pytest -m integration            # Run only integration tests
pytest -v                        # Verbose output

# Database migrations (uses Alembic)
alembic upgrade head             # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### NestJS Gateway (packages/nestjs-gateway/):

```bash
cd packages/nestjs-gateway

# Development
npm run start:dev                # Start with hot reload
npm run start:debug              # Start with debugger

# Testing
npm run test                     # Run unit tests
npm run test:watch               # Run tests in watch mode
npm run test:cov                 # Run tests with coverage
npm run test:e2e                 # Run end-to-end tests

# Build and production
npm run build                    # Build for production
npm run start:prod               # Run production build

# Code quality
npm run lint                     # Run ESLint with auto-fix
npm run format                   # Format code with Prettier
```

### Client (packages/client/):

```bash
cd packages/client

# Development
npm run dev                      # Start dev server (port 5173)
npm run build                    # Build for production
npm run preview                  # Preview production build

# Storybook
npm run storybook                # Run Storybook dev server
npm run build-storybook          # Build Storybook static files
```

## Architecture Overview

**📋 Comprehensive architecture documentation is available in:**
- `ARCHITECTURE_REVIEW.md`: Complete architecture analysis with health score, findings, and improvement roadmap
- `ARCHITECTURE_DIAGRAMS.md`: 12 Mermaid diagrams covering system architecture, layer diagrams, and deployment
- `ARCHITECTURE_METRICS.md`: Quantitative metrics including file counts, service complexity, and performance indicators

### Request Flow

1. **Client** makes requests to the **NestJS Gateway** (port 3000)
2. **NestJS Gateway** proxies requests to **FastAPI Backend** (port 8080)
3. **FastAPI Backend** processes requests using:
   - OpenAI GPT-4 for text conversion and quality analysis
   - RAG (Retrieval-Augmented Generation) for knowledge base queries
   - PostgreSQL with PGVector for document storage and vector search

### Python Backend Architecture

The Python backend uses **dependency injection** (via `dependency_injector`) with a centralized container pattern:

- **Container** (`core/container.py`): Manages all service dependencies as singletons
- **Services** (`services/`): Business logic layer with specialized services:
  - `ConversionService`: Text tone/style conversion
  - `QualityAnalysisService`: Text quality scoring and analysis
  - `RAGService`: Facade for RAG operations, coordinates specialized RAG subservices
    - `RAGEmbedderManager`: Manages embedding operations
    - `RAGIngestionService`: Handles document ingestion and indexing
    - `RAGQueryService`: Processes RAG queries and retrieval
  - `UserPreferencesService`: User profile and preference management
  - `DocumentService`: PDF and document processing
- **Agents** (`agents/`): LangGraph-based agents for complex workflows (optional, requires langgraph dependency)
- **API Endpoints** (`api/v1/endpoints/`): FastAPI route handlers

All services are registered as singletons in the DI container with explicit dependency wiring for better testability and maintainability.

### Key Service Patterns

**Dependency Injection**: Services are wired in `main.py` via the Container:

```python
container.wire(modules=[
    "api.v1.endpoints.conversion",
    "api.v1.endpoints.quality",
    "api.v1.endpoints.rag",
    # etc.
])
```

**Database**: Uses SQLAlchemy 2.0 with Alembic for migrations. Models are in `database/models.py`.

**RAG Pipeline**:
- Documents are split and embedded using OpenAI embeddings
- Stored in PostgreSQL with PGVector extension
- Retrieved via similarity search for context-aware responses

### NestJS Gateway Architecture

The gateway is a simple proxy layer that:
- Validates requests using class-validator DTOs (`src/dto/`)
- Forwards requests to the Python backend via HttpService (axios)
- Handles errors globally via interceptors (`src/interceptors/`)
  - `ErrorInterceptor`: Centralized error handling for HttpException, AxiosError, and unexpected errors
  - `LoggingInterceptor`: Request/response logging with duration tracking
- Provides Swagger documentation at `/api`

**Important**: The gateway does NOT contain business logic - it's purely a proxy and validation layer. Controller endpoints are clean and focused on request/response handling, with all error handling delegated to global interceptors.

See `packages/nestjs-gateway/ERROR_HANDLING.md` for comprehensive error handling documentation.

### Frontend Architecture

React app using:
- **React Router** for routing (`Router.tsx`)
- **TanStack Query** for server state management
- **Radix UI** components with Tailwind CSS
- **Axios** for API calls via unified `api` object (`src/lib/api.ts`)

**API Client Pattern**: All API communication uses the centralized axios-based `api` object with consistent error handling and request configuration. Each method corresponds to a backend endpoint (e.g., `api.convertStyle()`, `api.analyzeQuality()`).

## Environment Variables

⚠️ **CRITICAL**: As of 2026-01-04, all mock modes have been removed. The application **REQUIRES** a valid OpenAI API key to run.

Both the NestJS gateway and Python backend require environment variables. Create `.env.local` in the project root with:

```bash
# OpenAI (REQUIRED - Application will not start without this)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chattoner

# Python Backend
HOST=0.0.0.0
PORT=8080
DEBUG=true

# NestJS Gateway
BACKEND_API_URL=http://127.0.0.1:8080
PORT=3000
```

For Python backend, also create `packages/python_backend/.env` (the code explicitly loads from parent directory in main.py).

### Required vs Optional

**Required:**
- `OPENAI_API_KEY` - Application fails on startup without this

**Optional:**
- `OPENAI_MODEL` - Defaults to "gpt-4o"
- `DATABASE_URL` - Can be constructed from individual DB_ variables
- `DEBUG` - Defaults to True

## Testing Strategy

### Python Backend Tests

Tests use pytest with async support and mocking:
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.rag`, `@pytest.mark.slow`
- Coverage reports generated in `coverage_html/`
- Test fixtures defined in `conftest.py`

### NestJS Gateway Tests

Tests use Jest with:
- Unit tests: `*.spec.ts` files alongside source
- E2E tests: `test/` directory with `jest-e2e.json` config
- Mocking via `@nestjs/testing` utilities

## Development Workflow

### Adding a New API Endpoint

1. **Create endpoint in Python backend**:
   - Add route handler in `packages/python_backend/api/v1/endpoints/`
   - Define schemas in `api/v1/schemas/`
   - Implement service logic in `services/`
   - Wire service in `core/container.py` if needed
   - Add router to `api/v1/router.py`

2. **Create proxy in NestJS gateway**:
   - Add DTO in `packages/nestjs-gateway/src/dto/`
   - Add route handler in `src/app.controller.ts` (no try-catch needed - handled by global interceptors)

3. **Update frontend**:
   - Add API call in `packages/client/src/lib/` or create hook in `hooks/`
   - Create UI components in `components/`
   - Add page in `pages/` and route in `Router.tsx`

### Working with RAG

RAG functionality follows a **Facade pattern** with specialized subservices:

**Main Service (Facade)**:
- `services/rag_service.py`: High-level RAG orchestration, coordinates all RAG operations

**Specialized Subservices** (in `services/rag/`):
- `rag_embedder_manager.py`: Manages embedding generation and configuration
- `rag_ingestion_service.py`: Handles document chunking and indexing into vector store
- `rag_query_service.py`: Processes queries and retrieval operations
- `vector_store_pg.py`: PostgreSQL vector store operations with PGVector

**Supporting Components**:
- `langchain_pipeline/`: LangChain integration (chains, retrievers, prompts)
- `services/document_service.py`: Document processing and metadata management

**Document ingestion flow**: PDF → text extraction → chunking (RAGIngestionService) → embedding (RAGEmbedderManager) → vector store (VectorStorePG)

**Query flow**: User question → embedding (RAGEmbedderManager) → similarity search (RAGQueryService) → context retrieval → LLM generation → response

All RAG services are registered in the DI container (`core/container.py`) as singletons and wired with proper dependencies.

### Database Migrations

Python backend uses Alembic. To modify schema:
1. Update models in `packages/python_backend/database/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `alembic upgrade head`

## Architecture Changes (2026-01-04)

### Mock Mode Removal

**All mock and fallback implementations have been removed** to ensure production code quality:

1. **OpenAIService** - No longer has mock mode. Always requires valid API key.
2. **RAGService** - No longer creates dependencies internally. All must be injected via DI container.
3. **RAGEmbedderManager** - No longer falls back to SimpleTextEmbedder. Only uses GPT embedder.
4. **SimpleTextEmbedder** - Deprecated with runtime warnings.

**Impact:**
- Application **will not start** without `OPENAI_API_KEY`
- RAG services **must be wired** in DI container
- All embeddings use OpenAI (consistent quality)
- Clear error messages on configuration issues

**See `MOCK_REMOVAL_SUMMARY.md` for complete details.**

### Dependency Injection Requirements

All services must be properly wired in `core/container.py`:

```python
# All RAG services must be registered
rag_embedder_manager = providers.Singleton(RAGEmbedderManager)
rag_ingestion_service = providers.Singleton(RAGIngestionService, ...)
rag_query_service = providers.Singleton(RAGQueryService, ...)
rag_service = providers.Singleton(
    RAGService,
    embedder_manager=rag_embedder_manager,
    ingestion_service=rag_ingestion_service,
    query_service=rag_query_service
)
```

**Never instantiate services directly** - always use the DI container.

## Known Issues and Patterns

### Optional Enterprise Features

Some features depend on `langgraph` which may not always be installed. The codebase handles this gracefully:
- `core/container.py` conditionally imports enterprise features
- `ENTERPRISE_FEATURES_AVAILABLE` flag controls feature availability
- Quality analysis has LLM fallbacks when agent features are unavailable

### CORS Configuration

- Python backend: Origins defined in `main.py` (`FRONT_ORIGINS`)
- NestJS gateway: Configured in `main.ts` (allows all origins in development)

### Session Management

Python backend uses `starlette.middleware.sessions.SessionMiddleware` with SECRET_KEY from environment.

### Monorepo Structure

This is an npm workspaces monorepo. Dependencies in the root `package.json` are shared across all packages. When adding dependencies to a specific package, `cd` into that package and install there.
