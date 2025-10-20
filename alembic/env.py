import os
import sys

# Add the project root directory to sys.path to enable importing modules from root-level directories like 'api'.
# This is necessary because Alembic's env.py runs from the 'alembic' subdirectory, and without this adjustment,
# it cannot access the application's models or configurations located at the project root. Why this approach:
# It provides a reliable, cross-platform way to resolve paths dynamically at runtime, aligning with Pragmatic
# Programmer principles for flexible environments and avoiding hard-coded paths that break portability.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import logging.config  # noqa: E402
from sqlalchemy import engine_from_config, pool  # noqa: E402
from alembic import context  # noqa: E402

from api.models import Base  # noqa: E402
from api.core.config import settings  # noqa: E402

# Point Alembic to the models for autogeneration of migration scripts by providing the metadata
# that reflects the current state of the database schema as defined in our models. Why this:
# Enables autodetection of schema changes (e.g., new columns like agent_support), supporting
# evolvable designs per Fowler refactoring principles and ensuring consistency in AI trust ledgers.
target_metadata = Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    logging.config.fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    This hardened version explicitly sets the SQLAlchemy URL from the application's
    configuration (settings.DATABASE_URL), overriding any implicit reading from alembic.ini.
    Why this explicit approach is more robust: It establishes the app's config as the single
    source of truth, preventing conflicts from duplicated or outdated INI settings. This enhances
    consistency across environments (e.g., dev/test/prod), improves security by centralizing
    sensitive creds (e.g., via env vars in settings), and simplifies testing/maintenance by
    decoupling from file-based configs (aligns with Pragmatic Programmer principles for
    configuration management and Martin Clean Code for avoiding magic values).
    """
    # Explicitly set the SQLAlchemy URL in the Alembic config from app settings
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
