ALTER TABLE company_user_feedback
ADD COLUMN IF NOT EXISTS grammar_score FLOAT,
ADD COLUMN IF NOT EXISTS formality_score FLOAT,
ADD COLUMN IF NOT EXISTS readability_score FLOAT,
ADD COLUMN IF NOT EXISTS protocol_score FLOAT,
ADD COLUMN IF NOT EXISTS compliance_score FLOAT;