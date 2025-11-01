-- Company and team communication profiles

CREATE TABLE IF NOT EXISTS company_comm_profiles (
  tenant_id uuid PRIMARY KEY,
  traits jsonb NOT NULL,
  policy_key text,
  defaults jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS team_comm_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  team_key text NOT NULL,
  traits jsonb NOT NULL,
  overrides jsonb,
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, team_key)
);

