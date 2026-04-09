"""Alembic migration environment configuration for MySQL async."""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import all models to ensure they're registered with Base.metadata
from app.models.base import Base
from app.models import (
    organisation,
    utilisateur,
    source_donnees,
    execution_etl,
    lot_donnees,
    anomalie_donnee,
    enregistrement_brut,
    staging,
    aliment,
    exercice,
    ref_type_entrainement,
    profil_utilisateur,
    journal_alimentaire,
    mesure_biometrique,
    seance_entrainement,
    instantane_sommeil_sante,
)

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow overriding DB URL via env (keeps app & migrations aligned)
_env_db_url = os.getenv("DATABASE_URL")
if _env_db_url:
    config.set_main_option("sqlalchemy.url", _env_db_url)

# Target metadata from SQLAlchemy models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without DB connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
