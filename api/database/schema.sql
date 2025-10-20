-- Fulcrum Ledger V7-Lite Schema
-- Optimized for MVP speed and future extensibility.

-- Create ENUM types first for data integrity.
-- Using "DO $$ BEGIN ... END $$;" makes the script re-runnable.
DO $$ BEGIN
    CREATE TYPE principal_type AS ENUM ('human', 'agent', 'service');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE event_status AS ENUM ('active', 'amended', 'retracted');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- Lookup table for event types.
CREATE TABLE IF NOT EXISTS event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Table for principals (the actors in the system).
CREATE TABLE IF NOT EXISTS principals (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type principal_type NOT NULL,
    tenant_id UUID NULL, -- Kept for future multi-tenancy toggle
    created_at TIMESTAMPTZ DEFAULT now()
);


-- The core "events" table. This is the Trust Ledger.
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY,
    tenant_id UUID NULL,
    event_type_id INT NOT NULL REFERENCES event_types(id),
    event_type_name VARCHAR(100) NOT NULL, -- Denormalized for simple queries
    principal_id UUID NOT NULL REFERENCES principals(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    data JSONB NOT NULL,
    canonical_hash TEXT UNIQUE NOT NULL,
    previous_event_hash TEXT NULL, -- Hook for future immutability toggle
    status event_status NOT NULL DEFAULT 'active',
    amends_event_id UUID NULL REFERENCES events(id)
) PARTITION BY RANGE (timestamp);

-- Create indexes for common query patterns.
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_event_type_id ON events(event_type_id);
CREATE INDEX IF NOT EXISTS idx_events_principal_id ON events(principal_id);
CREATE INDEX IF NOT EXISTS idx_events_data_gin ON events USING GIN (data);

-- Note on Partitions:
-- We will create partitions manually or via an automated script as needed.
-- Example for next month:
-- CREATE TABLE events_2025_11 PARTITION OF events FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
