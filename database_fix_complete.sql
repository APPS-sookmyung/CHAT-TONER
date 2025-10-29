-- 완전한 데이터베이스 문제 해결 SQL
-- 모든 테이블 스키마 수정 및 테스트 데이터 생성

-- 1. company_profiles 테이블에 누락된 컬럼들 추가
ALTER TABLE company_profiles
ADD COLUMN IF NOT EXISTS survey_data JSONB,
ADD COLUMN IF NOT EXISTS communication_guidelines JSONB,
ADD COLUMN IF NOT EXISTS tone_preferences JSONB;

-- 2. company_user_feedback 테이블에 누락된 컬럼들 추가
ALTER TABLE company_user_feedback
ADD COLUMN IF NOT EXISTS grammar_score NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS formality_score NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS readability_score NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS protocol_score NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS compliance_score NUMERIC(5,2);

-- 3. Vector 확장 설치 (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 3. 누락된 테이블 생성
CREATE TABLE IF NOT EXISTS style_profile_index (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    company_id VARCHAR(255),
    profile_data JSONB NOT NULL,
    embedding VECTOR(1536), -- OpenAI ada-002 임베딩 차원
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. companies 테이블이 없으면 생성
CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    industry VARCHAR(255),
    business_description TEXT,
    team_size INTEGER,
    communication_style VARCHAR(100),
    main_channels TEXT[],
    main_targets TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. 테스트 기업 데이터 생성
INSERT INTO companies (id, name, industry, business_description, team_size, communication_style, main_channels, main_targets, created_at, updated_at)
VALUES ('test-company-001', 'Test Company', 'Technology', 'Software Development', 10, 'formal', ARRAY['email', 'slack'], ARRAY['internal', 'external'], NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    industry = EXCLUDED.industry,
    business_description = EXCLUDED.business_description,
    team_size = EXCLUDED.team_size,
    communication_style = EXCLUDED.communication_style,
    main_channels = EXCLUDED.main_channels,
    main_targets = EXCLUDED.main_targets,
    updated_at = NOW();

-- 6. 기업 프로필 데이터 생성
INSERT INTO company_profiles (company_id, survey_data, communication_guidelines, tone_preferences, created_at, updated_at)
VALUES ('test-company-001',
    '{"communication_style": "formal", "main_channels": ["email", "slack"], "team_size": 10, "industry": "Technology"}',
    '{"formality": "high", "tone": "professional", "preferred_greeting": "안녕하세요"}',
    '{"default_tone": "formal", "preferred_style": "concise", "avoid_slang": true}',
    NOW(), NOW())
ON CONFLICT (company_id) DO UPDATE SET
    survey_data = EXCLUDED.survey_data,
    communication_guidelines = EXCLUDED.communication_guidelines,
    tone_preferences = EXCLUDED.tone_preferences,
    updated_at = NOW();

-- 7. 사용자-기업 관계 생성
INSERT INTO user_company_preferences (user_id, company_id, preferences, created_at, updated_at)
VALUES ('e2e-test-user-001', 'test-company-001',
    '{"role": "developer", "department": "engineering", "communication_preference": "direct"}',
    NOW(), NOW())
ON CONFLICT (user_id, company_id) DO UPDATE SET
    preferences = EXCLUDED.preferences,
    updated_at = NOW();

-- 8. 커뮤니케이션 가이드라인 생성
INSERT INTO communication_guidelines (company_id, target_audience, context_type, guidelines, created_at, updated_at)
VALUES
('test-company-001', '팀동료', '보고서',
    '{"tone": "formal", "structure": ["제목", "요약", "본문", "결론"], "required_sections": ["executive_summary"]}',
    NOW(), NOW()),
('test-company-001', '직속상사', '이메일',
    '{"tone": "respectful", "greeting": "안녕하세요", "closing": "감사합니다"}',
    NOW(), NOW())
ON CONFLICT (company_id, target_audience, context_type) DO UPDATE SET
    guidelines = EXCLUDED.guidelines,
    updated_at = NOW();

-- 9. 사용자 데이터 생성 (프로필 저장을 위한 전제조건)
INSERT INTO users (id, email, name, created_at, updated_at)
VALUES
('e2e-test-user-001', 'test@example.com', 'Test User', NOW(), NOW()),
('test-user', 'test2@example.com', 'Test User 2', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    updated_at = NOW();

-- 10. 권한 부여 (chattoner-user에게 모든 테이블 접근 권한)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "chattoner-user";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "chattoner-user";
GRANT USAGE ON SCHEMA public TO "chattoner-user";

-- 11. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_companies_id ON companies(id);
CREATE INDEX IF NOT EXISTS idx_company_profiles_company_id ON company_profiles(company_id);
CREATE INDEX IF NOT EXISTS idx_user_company_prefs_user_company ON user_company_preferences(user_id, company_id);
CREATE INDEX IF NOT EXISTS idx_communication_guidelines_company ON communication_guidelines(company_id);
CREATE INDEX IF NOT EXISTS idx_style_profile_user_company ON style_profile_index(user_id, company_id);

-- 12. 확인 쿼리들
SELECT 'companies' as table_name, COUNT(*) as record_count FROM companies WHERE id = 'test-company-001'
UNION ALL
SELECT 'company_profiles' as table_name, COUNT(*) as record_count FROM company_profiles WHERE company_id = 'test-company-001'
UNION ALL
SELECT 'users' as table_name, COUNT(*) as record_count FROM users WHERE id IN ('e2e-test-user-001', 'test-user')
UNION ALL
SELECT 'user_company_preferences' as table_name, COUNT(*) as record_count FROM user_company_preferences WHERE company_id = 'test-company-001'
UNION ALL
SELECT 'communication_guidelines' as table_name, COUNT(*) as record_count FROM communication_guidelines WHERE company_id = 'test-company-001';

-- 13. 테이블 구조 확인
\d+ company_profiles;
\d+ company_user_feedback;
\d+ style_profile_index;