import os
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from sigma_finance.models import db

# Alembic Config object
config = context.config

# Set up Python logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set SQLAlchemy URL from environment or fallback
def get_engine_url():
    return os.getenv("DATABASE_URL", "sqlite:///instance/sigma.db").replace('%', '%%')

config.set_main_option("sqlalchemy.url", get_engine_url())

# Target metadata for autogenerate support
target_metadata = db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()