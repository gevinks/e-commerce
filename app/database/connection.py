from sqlalchemy import create_engine
from app.core.config import get_db_url, db_settings
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator

def create_db_engine():

    DATABASE_URL = get_db_url()

    is_sqlite = DATABASE_URL.startswith("sqlite")
    is_postgres = DATABASE_URL.startswith("postgres")

    engine_args = {
        "echo" : True
    }

    if is_sqlite:
        engine_args = {
            "connect_args" : {
                "check_same_thread": db_settings.sqlite_check_same_thread
            },
            "echo": db_settings.sqlite_echo
        }
    
    return create_engine(
        DATABASE_URL,
        **engine_args
    )

engine = create_db_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    db_session = SessionLocal()
    try:
        yield db_session
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

def create_db_tables():
    Base.metadata.create_all(bind=engine)

create_db_engine()