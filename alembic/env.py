from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text

from alembic import context
from app.core.settings import settings
from app.db.base import Base
from app.models import role_model  # noqa: F401
from app.models import product_model  # noqa: F401
from app.models import user_model  # noqa: F401
from app.models import password_reset_log_model  # noqa: F401
from app.models import user_session_model  # noqa: F401
from app.models import system_config_model  # noqa: F401
from app.models import icon_model  # noqa: F401
from app.models import dynamic_route_model  # noqa: F401
from app.models import app_config_global_model  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = settings.resolved_database_url
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
    render_as_batch = url.startswith("sqlite")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=render_as_batch,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    render_as_batch = database_url.startswith("sqlite")
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        if database_url.startswith(("mariadb", "mysql")):
            connection.execute(text(f"SET time_zone = '{settings.db_timezone}'"))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=render_as_batch,
            # En MariaDB/MySQL el DDL es auto-commit, por lo que necesitamos
            # hacer commit del registro de versión explícitamente.
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()

        # Forzar commit para garantizar que alembic_version se persista en MariaDB
        if database_url.startswith(("mariadb", "mysql")):
            connection.execute(text("COMMIT"))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
