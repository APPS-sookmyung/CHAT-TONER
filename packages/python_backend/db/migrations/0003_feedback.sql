-- User feedback tracking

CREATE TABLE IF NOT EXISTS user_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid,
  user_id uuid,
  suggestion_id text NOT NULL,
  decision text NOT NULL, -- good|bad
  context jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

