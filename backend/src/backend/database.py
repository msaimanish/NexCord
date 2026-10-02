from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings


engine = create_engine(
    settings.database_url,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)