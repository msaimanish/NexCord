from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from pgvector.psycopg import register_vector

from backend.config import settings


engine = create_engine(
    settings.database_url,
    echo=True,
)


@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    register_vector(dbapi_connection)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)