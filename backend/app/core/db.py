from sqlmodel import Session, create_engine

from app.core.config import settings

DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+psycopg://"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

def get_session():
    with Session(engine) as session:
        yield session