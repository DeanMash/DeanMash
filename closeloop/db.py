from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from closeloop.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_url() -> str:
    return get_settings().database_url


def build_engine(url: str | None = None):
    db_url = url or _engine_url()
    if db_url.startswith("sqlite"):
        # :memory: needs StaticPool so all sessions share one DB
        if ":memory:" in db_url:
            return create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        return create_engine(db_url, connect_args={"check_same_thread": False})
    return create_engine(db_url)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db(url: str | None = None) -> None:
    global engine, SessionLocal
    if url is not None:
        engine = build_engine(url)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    from closeloop import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()