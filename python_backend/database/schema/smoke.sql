-- smoke.sql
SELECT 1 AS ok;

INSERT INTO users (email, name)
VALUES ('smoke@example.com','Smoke')
ON CONFLICT (email) DO NOTHING;

SELECT id, email, created_at
FROM users
WHERE email IN ('admin@example.com','smoke@example.com')
ORDER BY id DESC
LIMIT 5;

-- (프로젝트 안 쓰면 project_id는 NULL로 둬도 됨)
WITH u AS (
  SELECT id AS user_id FROM users WHERE email='smoke@example.com' LIMIT 1
)
INSERT INTO artifacts (project_id, kind, uri, mime, size_bytes, meta, created_by)
SELECT NULL, 'input', 'gs://bucket/sample.jsonl', 'application/json', 12345,
       '{"samples": 100}'::jsonb, u.user_id
FROM u
RETURNING id;

WITH a AS (
  SELECT id FROM artifacts WHERE kind='input' ORDER BY id DESC LIMIT 1
), u AS (
  SELECT id AS user_id FROM users WHERE email='smoke@example.com' LIMIT 1
)
INSERT INTO conversion_jobs (project_id, input_artifact_id, output_format, params, status, created_by)
SELECT NULL, a.id, 'parquet', '{"shuffle": true}'::jsonb, 'queued', u.user_id
FROM a, u
RETURNING id, status;

SELECT id, status, created_at
FROM conversion_jobs
ORDER BY id DESC
LIMIT 5;
