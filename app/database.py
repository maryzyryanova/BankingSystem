import os

from dotenv import load_dotenv
from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

url_object = URL.create(
    os.getenv('DATABASE'),
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
)
engine = create_engine(url_object)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)