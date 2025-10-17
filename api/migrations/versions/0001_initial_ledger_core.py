"""Create initial interaction_log table for V9 Synapse Ledger Core

Revision ID: 0001_initial_ledger_core
Revises:
Create Date: 2025-10-17 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, BYTEA, TIMESTAMP
from datetime import date

# revision identifiers, used by Alembic.
revision = "0001_initial_ledger_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade function to create the partitioned interaction_log table,
    initial monthly partitions, primary key, unique constraint, and indexes.
    """
    # Create the partitioned table (no data insertion here)
    op.create_table(
        "interaction_log",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("agent_id", UUID(as_uuid=True), nullable=False),
        sa.Column("environment_hash", sa.TEXT(), nullable=False),
        sa.Column("causality_id", UUID(as_uuid=True), nullable=True),
        sa.Column("emitted_at_utc", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("action_type", sa.INTEGER(), nullable=False),
        sa.Column("payload", BYTEA(), nullable=False),
        sa.Column("payload_hash", sa.TEXT(), nullable=False),
        postgresql_partition_by="RANGE (emitted_at_utc)",
    )

    # Create initial monthly partitions for 2025 and 2026 (extend as needed in future migrations)
    for year in [2025, 2026]:
        for month in range(1, 13):
            start_date = date(year, month, 1)
            next_month = month + 1
            next_year = year
            if next_month > 12:
                next_month = 1
                next_year += 1
            end_date = date(next_year, next_month, 1)
            partition_name = f"interaction_log_{year}_{month:02d}"
            op.execute(
                f"CREATE TABLE {partition_name} PARTITION OF interaction_log "
                f"FOR VALUES FROM ('{start_date}') TO ('{end_date}');"
            )

    # Create primary key (must include partition key for partitioned tables)
    op.create_primary_key(
        "interaction_log_pkey", "interaction_log", ["id", "emitted_at_utc"]
    )

    # Create unique constraint for idempotency (must include partition key)
    op.create_unique_constraint(
        "interaction_log_payload_hash_key",
        "interaction_log",
        ["payload_hash", "emitted_at_utc"],
    )

    # Create standard indexes
    op.create_index(
        "ix_interaction_log_agent_id", "interaction_log", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_interaction_log_environment_hash",
        "interaction_log",
        ["environment_hash"],
        unique=False,
    )
    op.create_index(
        "ix_interaction_log_causality_id",
        "interaction_log",
        ["causality_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade function to drop indexes, constraints, partitions, and the table.
    Drops in reverse order for dependency safety.
    """
    # Drop indexes
    op.drop_index(
        "ix_interaction_log_causality_id", table_name="interaction_log", if_exists=True
    )
    op.drop_index(
        "ix_interaction_log_environment_hash",
        table_name="interaction_log",
        if_exists=True,
    )
    op.drop_index(
        "ix_interaction_log_agent_id", table_name="interaction_log", if_exists=True
    )

    # Drop unique constraint
    op.drop_constraint(
        "interaction_log_payload_hash_key",
        "interaction_log",
        type_="unique",
        if_exists=True,
    )

    # Drop primary key
    op.drop_constraint(
        "interaction_log_pkey", "interaction_log", type_="primary", if_exists=True
    )

    # Drop partitions (in reverse order to avoid issues, though not strictly necessary)
    for year in [2026, 2025]:  # Reverse years
        for month in range(12, 0, -1):  # Reverse months
            partition_name = f"interaction_log_{year}_{month:02d}"
            op.execute(f"DROP TABLE IF EXISTS {partition_name};")

    # Drop the main table (now empty of partitions)
    op.drop_table("interaction_log")
