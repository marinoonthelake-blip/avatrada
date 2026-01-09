CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE side_type AS ENUM ('BUY', 'SELL');
CREATE TYPE signal_source_enum AS ENUM ('ALGO_GAMMA', 'ALGO_SENTIMENT', 'AI_GEMINI', 'MANUAL_USER');

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    event_timestamp TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    trace_id UUID DEFAULT uuid_generate_v4()
);

CREATE OR REPLACE FUNCTION prevent_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'DIAMOND_PROTOCOL_VIOLATION: Mutation of immutable records is forbidden.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_log_immutable
BEFORE UPDATE OR DELETE ON audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_modification();
