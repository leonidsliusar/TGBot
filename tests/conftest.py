import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database
from sql_schema import Base


load_dotenv()
login = os.getenv('DB_LOGIN')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
db_name = 'db_test'


@pytest.fixture
def setup_and_teardown_db(monkeypatch):
    mock_engine = create_engine(f'postgresql://{login}:{password}@{host}/{db_name}')
    monkeypatch.setenv('DB_NAME', db_name)
    create_database(mock_engine.url)
    Base.metadata.create_all(mock_engine)
    mock_session = Session(mock_engine)
    yield mock_session
    Base.metadata.drop_all(mock_engine)
    drop_database(mock_engine.url)


class MockObjChat:
    def __init__(self, chat_id):
        self.id = chat_id


class MockMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = MockObjChat(chat_id)


@pytest.fixture
def mock_message():
    def wrapper(text, chat_id):
        return MockMessage(text, chat_id)
    return wrapper


@pytest.fixture
def mock_func():
    def wrapper(message):
        return message.text
    return wrapper
