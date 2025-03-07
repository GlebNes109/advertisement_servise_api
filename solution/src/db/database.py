from sqlalchemy import create_engine
from sqlmodel import SQLModel
from ..config import settings

DATABASE_URL = f"postgresql://{settings.postgres_username}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}"
print(f"DATABASE_URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
print("postgres connected")
SQLModel.metadata.create_all(engine)