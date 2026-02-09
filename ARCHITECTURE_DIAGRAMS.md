# Chat-Toner Architecture Diagrams

**Generated:** 2026-01-03
**Purpose:** Visual architecture documentation

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        ReactApp[React Application<br/>Port 5173]
    end

    subgraph "API Layer"
        Gateway[NestJS Gateway<br/>Port 3000]
        Validation[DTO Validation]
    end

    subgraph "Business Logic Layer"
        Backend[FastAPI Backend<br/>Port 8080]
        Services[Service Layer]
        Container[DI Container]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>+ PGVector)]
        Cache[(Redis<br/>Future)]
    end

    subgraph "External"
        OpenAI[OpenAI API]
    end

    Browser --> ReactApp
    ReactApp -->|HTTP/JSON| Gateway
    Gateway --> Validation
    Validation -->|Proxy| Backend
    Backend --> Container
    Container --> Services
    Services --> DB
    Services --> Cache
    Services --> OpenAI

    style ReactApp fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style Gateway fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    style Backend fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style DB fill:#fce4ec,stroke:#c2185b,stroke-width:3px
```

---

## 2. Detailed Component Diagram

```mermaid
graph TB
    subgraph "Frontend (packages/client)"
        Pages[Pages]
        Components[Components]
        Hooks[React Hooks]
        APIClient[API Client<br/>axios]
        Query[TanStack Query]
    end

    subgraph "Gateway (packages/nestjs-gateway)"
        Controller[AppController]
        DTOs[DTOs]
        HttpService[HttpService]
        ErrorHandler[Error Handler]
    end

    subgraph "Backend (packages/python_backend)"
        Router[API Router v1]
        Endpoints[Endpoints]
        Schemas[Pydantic Schemas]
    end

    subgraph "Services"
        Conversion[ConversionService]
        Quality[QualityAnalysisService]
        RAG[RAGService]
        Document[DocumentService]
        UserPref[UserPreferencesService]
        Profile[ProfileGeneratorService]
        PDF[PDFSummaryService]
    end

    subgraph "Core"
        DIContainer[DI Container]
        Config[Settings/Config]
        Middleware[Middleware]
    end

    subgraph "Infrastructure"
        DBStorage[DatabaseStorage]
        Models[SQLAlchemy Models]
        VectorStore[Vector Store PG]
        LangChain[LangChain Pipeline]
    end

    Pages --> Hooks
    Hooks --> Query
    Query --> APIClient
    APIClient --> Controller
    Controller --> DTOs
    DTOs --> HttpService
    HttpService --> Router
    Router --> Endpoints
    Endpoints --> Schemas
    Endpoints --> DIContainer
    DIContainer --> Conversion
    DIContainer --> Quality
    DIContainer --> RAG
    DIContainer --> Document
    DIContainer --> UserPref
    DIContainer --> Profile
    DIContainer --> PDF
    Conversion --> Config
    Quality --> Config
    RAG --> VectorStore
    RAG --> LangChain
    Document --> DBStorage
    UserPref --> DBStorage
    DBStorage --> Models
    Router --> Middleware

    style DIContainer fill:#fff3e0,stroke:#f57c00,stroke-width:4px
    style APIClient fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style Router fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
```

---

## 3. Layer Architecture (Python Backend)

```mermaid
graph TD
    subgraph "Layer 1: Presentation"
        API[API Endpoints<br/>api/v1/endpoints/*.py]
        Schemas[Pydantic Schemas<br/>api/v1/schemas/*.py]
    end

    subgraph "Layer 2: Application"
        Services[Services<br/>services/*.py]
        DI[DI Container<br/>core/container.py]
        Middleware[Middleware<br/>core/middleware.py]
    end

    subgraph "Layer 3: Domain"
        Models[Domain Models<br/>database/models.py]
        Logic[Business Logic]
        Utils[Utilities<br/>utils/*.py]
    end

    subgraph "Layer 4: Infrastructure"
        DB[Database Access<br/>database/db.py]
        Storage[Storage Layer<br/>database/storage.py]
        External[External APIs<br/>OpenAI, etc.]
        LangChain[LangChain Pipeline<br/>langchain_pipeline/*]
    end

    API --> Schemas
    Schemas --> Services
    Services --> DI
    API --> Middleware
    DI --> Models
    Services --> Logic
    Services --> Utils
    Logic --> Models
    Services --> DB
    Services --> Storage
    Services --> External
    Services --> LangChain
    Storage --> DB

    style API fill:#bbdefb,stroke:#0288d1,stroke-width:3px
    style Services fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Models fill:#fff9c4,stroke:#f57c00,stroke-width:3px
    style DB fill:#ffccbc,stroke:#c2185b,stroke-width:3px
```

---

## 4. Request Flow Sequence

```mermaid
sequenceDiagram
    participant User as User Browser
    participant React as React App
    participant Gateway as NestJS Gateway
    participant FastAPI as FastAPI Backend
    participant Container as DI Container
    participant Service as ConversionService
    participant OpenAI as OpenAI API
    participant DB as PostgreSQL

    User->>React: Enter text to convert
    React->>React: Validate input
    React->>Gateway: POST /api/v1/conversion/convert
    Note over Gateway: Validate with DTO
    Gateway->>FastAPI: Proxy request
    FastAPI->>FastAPI: Route to endpoint
    FastAPI->>Container: Resolve dependencies
    Container->>Service: Inject dependencies
    FastAPI->>Service: convert_text(request)
    Service->>Service: Prepare prompt
    Service->>OpenAI: Generate completion
    OpenAI-->>Service: Converted text
    Service->>DB: Save conversion history
    DB-->>Service: Success
    Service-->>FastAPI: ConversionResult
    FastAPI-->>Gateway: JSON response
    Gateway-->>React: ConversionResponseDto
    React-->>User: Display result
```

---

## 5. RAG Pipeline Architecture

```mermaid
graph LR
    subgraph "Document Ingestion"
        Upload[Document Upload]
        Extract[Text Extraction]
        Chunk[Text Chunking]
        Embed[Embedding Generation]
        Store[Vector Store]
    end

    subgraph "Query Processing"
        Question[User Question]
        QueryEmbed[Query Embedding]
        Search[Similarity Search]
        Retrieve[Retrieve Context]
        Generate[LLM Generation]
        Response[Final Answer]
    end

    subgraph "RAG Services"
        Ingestion[RAGIngestionService]
        Query[RAGQueryService]
        Embedder[RAGEmbedderManager]
    end

    Upload --> Extract
    Extract --> Chunk
    Chunk --> Ingestion
    Ingestion --> Embed
    Embed --> Embedder
    Embedder --> Store

    Question --> QueryEmbed
    QueryEmbed --> Query
    Query --> Search
    Search --> Store
    Store --> Retrieve
    Retrieve --> Generate
    Generate --> Response

    style Ingestion fill:#c8e6c9,stroke:#388e3c
    style Query fill:#bbdefb,stroke:#0288d1
    style Embedder fill:#fff9c4,stroke:#f57c00
    style Store fill:#ffccbc,stroke:#c2185b
```

---

## 6. Dependency Injection Graph

```mermaid
graph TD
    Container[DI Container]

    Container --> Settings[Settings]
    Container --> PromptEngineer[PromptEngineer]
    Container --> OpenAI[OpenAIService]
    Container --> DBStorage[DatabaseStorage]

    Container --> Conversion[ConversionService]
    Container --> UserPref[UserPreferencesService]
    Container --> Document[DocumentService]
    Container --> RAG[RAGService]
    Container --> Profile[ProfileGeneratorService]
    Container --> PDF[PDFSummaryService]

    Conversion --> PromptEngineer
    Conversion --> OpenAI
    UserPref --> DBStorage
    UserPref --> OpenAI
    Document --> Settings
    Profile --> OpenAI
    PDF --> OpenAI

    subgraph "Optional Enterprise"
        Container -.-> EnterprisDB[EnterpriseDBService]
        Container -.-> QualityAgent[OptimizedEnterpriseQualityAgent]
        Container -.-> QualityService[OptimizedEnterpriseQualityService]
        QualityAgent -.-> RAG
        QualityAgent -.-> EnterprisDB
    end

    style Container fill:#fff3e0,stroke:#f57c00,stroke-width:4px
    style Settings fill:#e8f5e9,stroke:#388e3c
    style OpenAI fill:#e1f5ff,stroke:#0288d1
    style EnterprisDB stroke-dasharray: 5 5
    style QualityAgent stroke-dasharray: 5 5
    style QualityService stroke-dasharray: 5 5
```

---

## 7. Data Model Relationships

```mermaid
erDiagram
    USER_PROFILES ||--o{ CONVERSION_HISTORY : has
    USER_PROFILES ||--o{ USER_SURVEYS : completes
    COMPANY_PROFILES ||--o{ COMPANY_POLICIES : defines
    COMPANY_PROFILES ||--o{ QUALITY_ANALYSIS : requests
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : contains
    DOCUMENT_CHUNKS ||--|| VECTOR_EMBEDDINGS : has

    USER_PROFILES {
        string user_id PK
        json style_preferences
        int level
        string tone_preference
        timestamp created_at
    }

    CONVERSION_HISTORY {
        int id PK
        string user_id FK
        text original_text
        text converted_text
        timestamp created_at
    }

    COMPANY_PROFILES {
        string company_id PK
        string name
        json writing_guidelines
        timestamp created_at
    }

    DOCUMENTS {
        int id PK
        string filename
        string document_type
        timestamp uploaded_at
    }

    DOCUMENT_CHUNKS {
        int id PK
        int document_id FK
        text content
        int chunk_index
    }

    VECTOR_EMBEDDINGS {
        int id PK
        int chunk_id FK
        vector embedding
    }
```

---

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph "Google Cloud Platform"
        subgraph "Cloud Run Services"
            ClientService[Client Service<br/>client-3yj2y7svbq-du]
            GatewayService[Gateway Service]
            BackendService[Backend Service]
        end

        subgraph "Data Services"
            CloudSQL[(Cloud SQL<br/>PostgreSQL + PGVector)]
            CloudStorage[Cloud Storage<br/>Documents]
        end

        LoadBalancer[Cloud Load Balancer]
    end

    subgraph "External Services"
        OpenAI[OpenAI API]
        DNS[DNS/Domain]
    end

    subgraph "Development"
        LocalClient[localhost:5173]
        LocalGateway[localhost:3000]
        LocalBackend[localhost:8080]
        LocalDB[(Local PostgreSQL)]
    end

    DNS --> LoadBalancer
    LoadBalancer --> ClientService
    LoadBalancer --> GatewayService
    ClientService --> GatewayService
    GatewayService --> BackendService
    BackendService --> CloudSQL
    BackendService --> CloudStorage
    BackendService --> OpenAI

    style ClientService fill:#e8f5e9,stroke:#388e3c
    style GatewayService fill:#e1f5ff,stroke:#0288d1
    style BackendService fill:#fff3e0,stroke:#f57c00
    style CloudSQL fill:#fce4ec,stroke:#c2185b
```

---

## 9. Error Handling Flow

```mermaid
graph TD
    Request[Incoming Request]
    Gateway[Gateway Validation]
    Backend[Backend Processing]
    Service[Service Logic]

    Request --> Gateway
    Gateway -->|Valid| Backend
    Gateway -->|Invalid| GatewayError[DTO Validation Error]
    Backend --> Service
    Service -->|Success| Success[Success Response]
    Service -->|Error| ServiceError[Service Error]

    GatewayError --> ErrorInterceptor[Error Interceptor<br/>Future]
    ServiceError --> ErrorHandler[Exception Handler]
    ErrorHandler --> LogError[Log Error]
    ErrorInterceptor --> LogError
    LogError --> ErrorResponse[Error Response]

    ErrorResponse --> Client[Client Error Display]
    Success --> Client

    style GatewayError fill:#ffcdd2,stroke:#c62828
    style ServiceError fill:#ffcdd2,stroke:#c62828
    style ErrorResponse fill:#ffcdd2,stroke:#c62828
    style Success fill:#c8e6c9,stroke:#388e3c
```

---

## 10. Monorepo Structure

```mermaid
graph TD
    Root[chattoner-monorepo<br/>package.json]

    Root --> Client[packages/client<br/>React + Vite]
    Root --> Gateway[packages/nestjs-gateway<br/>NestJS]
    Root --> Backend[packages/python_backend<br/>FastAPI]
    Root --> Scripts[scripts/]
    Root --> Docs[Documentation<br/>CLAUDE.md, README.md]

    Client --> ClientSrc[src/<br/>components, pages, hooks]
    Client --> ClientConfig[Config<br/>vite.config.ts, tsconfig.json]
    Client --> ClientDeps[package.json]

    Gateway --> GatewaySrc[src/<br/>controllers, dto, modules]
    Gateway --> GatewayConfig[Config<br/>nest-cli.json, tsconfig.json]
    Gateway --> GatewayDeps[package.json]

    Backend --> BackendAPI[api/<br/>endpoints, schemas]
    Backend --> BackendServices[services/]
    Backend --> BackendCore[core/<br/>container, config]
    Backend --> BackendDB[database/<br/>models, storage]
    Backend --> BackendTests[tests/]
    Backend --> BackendDeps[requirements.txt]

    style Root fill:#fff3e0,stroke:#f57c00,stroke-width:4px
    style Client fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style Gateway fill:#e1f5ff,stroke:#0288d1,stroke-width:3px
    style Backend fill:#ffecb3,stroke:#ffa000,stroke-width:3px
```

---

## 11. Service Communication Patterns

```mermaid
graph LR
    subgraph "Synchronous Communication"
        Frontend[Frontend]
        Gateway[Gateway]
        Backend[Backend]
        DB[(Database)]

        Frontend -->|HTTP Request| Gateway
        Gateway -->|HTTP Proxy| Backend
        Backend -->|Query| DB
        DB -->|Result| Backend
        Backend -->|Response| Gateway
        Gateway -->|Response| Frontend
    end

    subgraph "External Communication"
        Backend -->|API Call| OpenAI[OpenAI API]
        OpenAI -->|Response| Backend
    end

    style Frontend fill:#e8f5e9,stroke:#388e3c
    style Gateway fill:#e1f5ff,stroke:#0288d1
    style Backend fill:#fff3e0,stroke:#f57c00
    style DB fill:#fce4ec,stroke:#c2185b
    style OpenAI fill:#f3e5f5,stroke:#7b1fa2
```

---

## 12. Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        Client[Client Application]
        CORS[CORS Middleware]
        Validation[Input Validation]
        Session[Session Middleware]
        Secrets[Environment Variables]
    end

    subgraph "Validation Points"
        DTOValidation[DTO Validation<br/>class-validator]
        SchemaValidation[Schema Validation<br/>Pydantic]
    end

    subgraph "Data Protection"
        EnvVars[.env Files]
        SecretManager[Secret Manager<br/>Future]
    end

    Client --> CORS
    CORS --> DTOValidation
    DTOValidation --> Session
    Session --> SchemaValidation
    SchemaValidation --> Services[Protected Services]

    Services --> EnvVars
    Services --> SecretManager

    style CORS fill:#c8e6c9,stroke:#388e3c
    style Validation fill:#c8e6c9,stroke:#388e3c
    style Session fill:#c8e6c9,stroke:#388e3c
    style DTOValidation fill:#bbdefb,stroke:#0288d1
    style SchemaValidation fill:#bbdefb,stroke:#0288d1
```

---

## Usage Notes

These diagrams provide visual documentation of the Chat-Toner architecture. They can be:

1. **Rendered** in any Mermaid-compatible viewer
2. **Embedded** in documentation
3. **Exported** to PNG/SVG for presentations
4. **Updated** as the architecture evolves

Refer to `ARCHITECTURE_REVIEW.md` for detailed analysis and `ARCHITECTURE_METRICS.md` for quantitative metrics.
