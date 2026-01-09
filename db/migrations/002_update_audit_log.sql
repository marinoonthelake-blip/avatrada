-- Add missing columns to audit_log
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS actor_id TEXT;
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS entity_id TEXT;

-- Add index for the new entity_id column for faster lookups
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_id);
