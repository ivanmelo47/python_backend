from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings

database_url = settings.resolved_database_url

engine_kwargs: dict = {"pool_pre_ping": True}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)

if database_url.startswith(("mariadb", "mysql")):
    @event.listens_for(engine, "connect")
    def set_db_timezone(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
        del connection_record
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f"SET time_zone = '{settings.db_timezone}'")
        finally:
            cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
