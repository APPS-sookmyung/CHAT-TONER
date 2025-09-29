-- init.sql (PostgreSQL)
-- SQLAlchemy 모델을 기반으로 하되, 데이터 정합성과 모범 사례를 적용하여 수정함

BEGIN;

-- 1. 사용자 테이블
-- PK 타입을 Integer 대신 64비트 정수인 BIGINT를 사용하는 BIGSERIAL로 변경하여 확장성 확보
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);


-- 2. 사용자 프로필 테이블
-- [수정] user_id 타입을 users.id와 일치하는 BIGINT로 변경하고 외래 키 제약조건 추가
-- [추가] 사용자가 삭제되면 프로필도 함께 삭제되도록 ON DELETE CASCADE 설정
CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    base_formality_level INTEGER DEFAULT 3,
    base_friendliness_level INTEGER DEFAULT 3,
    base_emotion_level INTEGER DEFAULT 3,
    base_directness_level INTEGER DEFAULT 3,
    session_formality_level REAL,
    session_friendliness_level REAL,
    session_emotion_level REAL,
    session_directness_level REAL,
    questionnaire_responses JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_user_profiles_id ON user_profiles(id);
CREATE INDEX IF NOT EXISTS ix_user_profiles_user_id ON user_profiles(user_id);


-- 3. 변환 기록 테이블
-- [수정] user_id 타입을 users.id와 일치하는 BIGINT로 변경하고 외래 키 제약조건 추가
-- [추가] 사용자가 삭제되어도 기록은 남도록 ON DELETE SET NULL 설정
CREATE TABLE IF NOT EXISTS conversion_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    original_text TEXT NOT NULL,
    converted_texts JSONB NOT NULL,
    context VARCHAR(50) DEFAULT 'personal',
    user_rating INTEGER,
    selected_version VARCHAR(20),
    feedback_text TEXT,
    sentiment_analysis JSONB DEFAULT '{}',
    prompts_used JSONB DEFAULT '{}',
    model_used VARCHAR(50) DEFAULT 'gpt-4o',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_conversion_history_id ON conversion_history(id);
CREATE INDEX IF NOT EXISTS ix_conversion_history_user_id ON conversion_history(user_id);


-- 4. 네거티브 프롬프트 설정 테이블
-- [수정] user_id 타입을 users.id와 일치하는 BIGINT로 변경하고 외래 키 제약조건 추가
CREATE TABLE IF NOT EXISTS negative_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    avoid_flowery_language VARCHAR(20) DEFAULT 'moderate',
    avoid_repetitive_words VARCHAR(20) DEFAULT 'moderate',
    comma_usage_style VARCHAR(20) DEFAULT 'moderate',
    content_over_format VARCHAR(20) DEFAULT 'moderate',
    bullet_point_usage VARCHAR(20) DEFAULT 'moderate',
    emoticon_usage VARCHAR(20) DEFAULT 'strict',
    custom_negative_prompts JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_negative_preferences_id ON negative_preferences(id);
CREATE INDEX IF NOT EXISTS ix_negative_preferences_user_id ON negative_preferences(user_id);


-- 5. 벡터 문서 메타데이터 테이블
CREATE TABLE IF NOT EXISTS vector_document_metadata (
    id BIGSERIAL PRIMARY KEY,
    document_hash VARCHAR(64) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text/plain',
    embedding_model VARCHAR(100) NOT NULL,
    chunk_count INTEGER NOT NULL,
    chunk_size INTEGER NOT NULL,
    chunk_overlap INTEGER NOT NULL,
    faiss_index_path TEXT NOT NULL,
    vector_dimension INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    last_accessed TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_vector_document_metadata_id ON vector_document_metadata(id);
CREATE INDEX IF NOT EXISTS ix_vector_document_metadata_document_hash ON vector_document_metadata(document_hash);


-- 6. RAG 질의 응답 기록 테이블
-- [수정] user_id 타입을 users.id와 일치하는 BIGINT로 변경하고 외래 키 제약조건 추가
CREATE TABLE IF NOT EXISTS rag_query_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    context_type VARCHAR(50) DEFAULT 'general',
    retrieved_documents JSONB DEFAULT '[]',
    similarity_scores JSONB DEFAULT '[]',
    total_search_time_ms INTEGER DEFAULT 0,
    generated_answer TEXT,
    answer_quality_score REAL,
    model_used VARCHAR(50) DEFAULT 'gpt-4',
    total_generation_time_ms INTEGER DEFAULT 0,
    user_rating INTEGER,
    user_feedback TEXT,
    was_helpful BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_rag_query_history_id ON rag_query_history(id);
CREATE INDEX IF NOT EXISTS ix_rag_query_history_user_id ON rag_query_history(user_id);
CREATE INDEX IF NOT EXISTS ix_rag_query_history_query_hash ON rag_query_history(query_hash);


-- 7. 기업 프로필 테이블
CREATE TABLE IF NOT EXISTS company_profiles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255),
    survey_data JSONB,
    generated_profile TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_company_profiles_id ON company_profiles(id);
CREATE INDEX IF NOT EXISTS ix_company_profiles_name ON company_profiles(name);


COMMIT;