-- 기업용 ChatToner 확장을 위한 새 테이블들
-- GUI에서 실행하세요: pgAdmin Query Tool 등

-- 1. 기업 프로필 테이블
CREATE TABLE IF NOT EXISTS company_profiles (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(100) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    team_size INTEGER,
    primary_business TEXT,
    communication_style VARCHAR(50), -- friendly, strict, formal
    main_channels JSONB, -- ["slack", "discord", "email"]
    target_audience JSONB, -- ["internal", "clients", "management"]
    generated_profile TEXT, -- LLM이 생성한 커뮤니케이션 프로필
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 커뮤니케이션 가이드라인 테이블
CREATE TABLE IF NOT EXISTS communication_guidelines (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(100) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- pdf, text, manual_input
    document_name VARCHAR(255),
    document_content TEXT NOT NULL,
    processed_chunks JSONB, -- 처리된 텍스트 청크와 임베딩
    uploaded_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 사용자 피드백 테이블 (기업 버전)
CREATE TABLE IF NOT EXISTS company_user_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100),
    original_text TEXT NOT NULL,
    suggested_text TEXT NOT NULL,
    feedback_type VARCHAR(20) NOT NULL, -- grammar, protocol
    feedback_value VARCHAR(10) NOT NULL, -- good, bad
    applied_in_final BOOLEAN DEFAULT FALSE,
    metadata JSONB, -- 컨텍스트 정보
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 기업 학습 데이터 테이블
CREATE TABLE IF NOT EXISTS company_learning_data (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    feedback VARCHAR(10), -- good, bad, neutral
    context JSONB, -- 상황, 대상, 채널 정보
    embedding JSONB, -- 벡터 임베딩
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 사용자 기업 선호도 테이블
CREATE TABLE IF NOT EXISTS user_company_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    personal_style JSONB, -- 개인 스타일 설정
    negative_prompts TEXT, -- 피하고 싶은 스타일
    preference_weights JSONB, -- 문법/프로토콜/개인 가중치
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, company_id)
);

-- 6. 사용자-기업 연결 테이블
CREATE TABLE IF NOT EXISTS user_company_relations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee', -- admin, hr, employee
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, pending
    onboarding_completed BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, company_id)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_company_profiles_company_id ON company_profiles(company_id);
CREATE INDEX IF NOT EXISTS idx_communication_guidelines_company_id ON communication_guidelines(company_id);
CREATE INDEX IF NOT EXISTS idx_company_user_feedback_company_id ON company_user_feedback(company_id);
CREATE INDEX IF NOT EXISTS idx_company_user_feedback_user_id ON company_user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_company_learning_data_company_id ON company_learning_data(company_id);
CREATE INDEX IF NOT EXISTS idx_user_company_preferences_user_company ON user_company_preferences(user_id, company_id);
CREATE INDEX IF NOT EXISTS idx_user_company_relations_user_company ON user_company_relations(user_id, company_id);

-- 외래 키 제약 조건 (기존 users 테이블과 연결)
-- 주의: 기존 users 테이블 구조를 확인 후 활성화하세요
-- ALTER TABLE company_user_feedback ADD CONSTRAINT fk_company_user_feedback_user
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
-- ALTER TABLE company_learning_data ADD CONSTRAINT fk_company_learning_data_user
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
-- ALTER TABLE user_company_preferences ADD CONSTRAINT fk_user_company_preferences_user
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
-- ALTER TABLE user_company_relations ADD CONSTRAINT fk_user_company_relations_user
--     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 테이블 생성 확인
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE '%company%'
ORDER BY table_name;

 -- 설문조사 응답 테이블 (새로 추가 필요)
  CREATE TABLE company_survey_responses (
      id SERIAL PRIMARY KEY,
      company_id VARCHAR(100) NOT NULL,
      respondent_name VARCHAR(255), -- 응답자 이름
      respondent_role VARCHAR(100), -- 응답자 역할 (HR, 팀리더 등)
      survey_responses JSONB NOT NULL, -- 설문 응답 데이터
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  2. communication_guidelines 테이블 수정

  벡터 임베딩 관련 컬럼 추가:
  ALTER TABLE communication_guidelines
  ADD COLUMN vector_embeddings JSONB,
  ADD COLUMN chunk_metadata JSONB;

  3. 동적 쿼리 관련 테이블 추가

  -- 쿼리 분석 결과 저장
  CREATE TABLE query_analysis_results (
      id SERIAL PRIMARY KEY,
      user_input TEXT NOT NULL,
      analyzed_metadata JSONB, -- 의도, 대상, 상황 분석
      company_id VARCHAR(100),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );