import asyncio
import os
import re

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, drop_database

import cache_module
from gpt import GPTFactoryAssistant
from sql_schema import Base


load_dotenv()
login = os.getenv('DB_LOGIN')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
db_name = 'db_test'


@pytest.fixture
def setup_and_teardown_db(monkeypatch):
    mock_engine = create_engine(f'postgresql://{login}:{password}@{host}/{db_name}')
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
async def mock_func():
    def wrapper(instance, message):
        return message.text
    return wrapper


@pytest.fixture
def mock_coroutine():
    async def wrapper(instance, message):
        return message.text
    return wrapper


class MockSession:
    __slots__ = ['url', 'data', 'headers', 'text', 'cookies']

    def __init__(self, text):
        self.url = None
        self.data = None
        self.headers = None
        self.text = text
        self.cookies = text

    async def post(self, url, data, headers):
        self.url = url
        self.data = data
        self.headers = headers

    def get(self, url):
        if url == 'Server Error':
            return MockResponse('500', self.text)
        else:
            return MockResponse('200', self.text)


class MockResponse:
    __slots__ = ['status_code', 'text']

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


class MockBeautifulSoup:
    def __init__(self, text, parser):
        self.text = text
        self.parser = parser
        self.a = MockBSTag()
        self.center = MockBSTag()
        self.div = MockBSTag()

    def find(self, *args):
        return self

    def find_all(self, *args):
        return [{'value': self.text}]

    def get_text(self, *args, **kwargs):
        return f'\"{self.text}\"'


class MockBSTag:

    def decompose(self):
        pass


@pytest.fixture
def set_session():
    async def wrapper(text):
        return MockSession(text)
    return wrapper


@pytest.fixture
def get_instance_mock_beauty_soup():
    return MockBeautifulSoup


@pytest.fixture
def mock_chat_response_writer():
    @cache_module.db_cache.set_cache
    async def wrapper(instance, message):
        pattern = re.compile('(Continue the story in the same style:)|\\s')
        mock_response = pattern.sub("", message.text)
        return mock_response
    return wrapper


class StubGPT:

    def __init__(self, text):
        self.choices = [{'message': {'content': 'stub response from stub chat'}}]

@pytest.fixture
def mock_chat_request_writer():
    async def wrapper(instance, message):
        response = StubGPT(message)
        return response
    return wrapper

