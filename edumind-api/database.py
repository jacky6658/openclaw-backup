from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/edumind")

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
