-- -- seed.sql
-- BEGIN;

-- INSERT INTO users (email, name)
-- VALUES ('admin@example.com','Admin')
-- ON CONFLICT (email) DO NOTHING;

-- INSERT INTO projects (owner_id, title)
-- SELECT id, 'default' FROM users WHERE email='admin@example.com'
-- ON CONFLICT DO NOTHING;

-- COMMIT;


-- seed.sql

BEGIN;

-- 1. 테스트 사용자 2명 추가
INSERT INTO users (email, name) VALUES
('test.user1@example.com', '김테스트'),
('test.user2@example.com', '박개발');

-- 2. 첫 번째 사용자(id=1)의 이름으로 프로젝트 생성
-- SERIAL로 생성된 사용자의 id가 1이라고 가정합니다.
INSERT INTO projects (owner_id, title) VALUES
(1, '나의 첫 AI 프로젝트');

-- 3. 위에서 생성한 프로젝트(id=1)에 대한 결과물(artifact) 데이터 추가
-- 마찬가지로 프로젝트 id가 1이라고 가정합니다.
INSERT INTO artifacts (project_id, kind, uri, created_by) VALUES
(1, 'input', 'gs://my-bucket/initial-data.zip', 1),
(1, 'output', 'gs://my-bucket/results/output.jsonl', 1);

COMMIT;