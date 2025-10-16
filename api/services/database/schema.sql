-- FULCRUM LEDGER SCHEMA V2
-- This script is idempotent and can be run safely.

-- Enable UUIDv7 support by creating the function if it doesn't exist.
-- This function is a standard, community-accepted implementation.
CREATE OR REPLACE FUNCTION uuid_generate_v7()
RETURNS UUID AS $$
BEGIN
    -- Example implementation, replace with a trusted one if available as an extension
    -- For simplicity, we'll use uuid_generate_v4() for now and flag this for upgrade
    -- In a real production environment, we would install an extension like 'pg_uuidv7'
    RETURN gen_random_uuid(); -- Placeholder using v4
END;
$$ LANGUAGE plpgsql;


-- Create ENUM types for controlled vocabularies
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


-- Create supporting tables first due to foreign key constraints

CREATE TABLE IF NOT EXISTS event_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS principals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    name VARCHAR(255) NOT NULL,
    type principal_type NOT NULL,
    tenant_id UUID,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_principals_tenant_id ON principals(tenant_id);


-- Create the core EVENTS table (Trust Ledger)
-- Partitioned by month on the timestamp for performance at scale.
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    tenant_id UUID,
    event_type_id INT NOT NULL REFERENCES event_types(id),
    event_type_name VARCHAR(100) NOT NULL, -- Denormalized for query performance
    principal_id UUID NOT NULL REFERENCES principals(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    data JSONB NOT NULL,
    canonical_hash TEXT UNIQUE NOT NULL,
    previous_event_hash TEXT,
    status event_status NOT NULL DEFAULT 'active',
    amends_event_id UUID REFERENCES events(id)
) PARTITION BY RANGE (timestamp);

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_events_tenant_id_timestamp ON events(tenant_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_event_type_id_timestamp ON events(event_type_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_principal_id_timestamp ON events(principal_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_data_gin ON events USING GIN (data);


-- Create the COSTS table (Cost Ledger)
CREATE TABLE IF NOT EXISTS costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    model_id VARCHAR(255),
    dataset_id VARCHAR(255),
    cost_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_costs_event_id ON costs(event_id);
CREATE INDEX IF NOT EXISTS idx_costs_model_id ON costs(model_id);
CREATE INDEX IF NOT EXISTS idx_costs_dataset_id ON costs(dataset_id);


-- Create the ANNOTATIONS table (Human Context Ledger)
CREATE TABLE IF NOT EXISTS annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    principal_id UUID NOT NULL REFERENCES principals(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    comment TEXT NOT NULL,
    data JSONB
);

CREATE INDEX IF NOT EXISTS idx_annotations_event_id ON annotations(event_id);

-- Note on partitions:
-- Partitions for the 'events' table need to be created manually or via an automated script.
-- Example for creating a partition for October 2024:
-- CREATE TABLE events_2024_10 PARTITION OF events FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
