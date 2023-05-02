import pytest
import parser
from parser import get_login, get_exercise, get_list_exercises


class MockSession:
    __slots__ = ['url', 'data', 'headers', 'text']

    def __init__(self, text):
        self.url = None
        self.data = None
        self.headers = None
        self.text = text

    def post(self, url, data, headers):
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

    def find(self, *args):
        return self

    def find_all(self, *args):
        return [{'value': self.text}]


class TestParser:
    @pytest.mark.parametrize('test_url, test_username, test_password, test_user_agent', [
        ('test_url', 'useruser', 'qwerty123456', 'Python'),
        (123, 123, 123, 456)
    ])
    def test_get_login_send_post(self, test_url, test_username, test_password, test_user_agent, monkeypatch):
        session = MockSession('pass')
        monkeypatch.setattr(parser, 'session', session)
        monkeypatch.setattr(parser, 'url', test_url)
        monkeypatch.setattr(parser, 'username', test_username)
        monkeypatch.setattr(parser, 'password', test_password)
        monkeypatch.setattr(parser, 'user_agent', test_user_agent)
        get_login()
        assert session.url == test_url
        assert session.data == {'login': test_username, 'psw': test_password}
        assert session.headers == {'user-agent': test_user_agent}

    @pytest.mark.parametrize('test_url, expected_result', [
                                                        ('Server Error', '5xx'),
                                                        ('some_url', 'tests')
    ])
    def test_get_list_exercises(self, test_url, expected_result, monkeypatch):
        session = MockSession(expected_result)
        monkeypatch.setattr(parser, 'session', session)
        monkeypatch.setattr(parser, 'url_questions', test_url)
        monkeypatch.setattr(parser, 'BeautifulSoup', MockBeautifulSoup)
        assert get_list_exercises() == expected_result + ';'
