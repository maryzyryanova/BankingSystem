from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine, Session


url_object = URL.create(
    "postgresql",
    username="postgres",
    password="mmz18102002zmm",
    host="localhost",
    database="banking_system",
)
engine = create_engine(url_object)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)