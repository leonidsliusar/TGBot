from cache_module import CacheDB
import pytest
import cache_module


class MockObjChat:
    def __init__(self, chat_id):
        self.id = chat_id


class MockMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = MockObjChat(chat_id)


def mock_message(text, chat_id):
    return MockMessage(text, chat_id)


def mock_func(message):
    return message.text


class TestDB:
    def test_set_get_cache(self, monkeypatch, setup_and_teardown, text='test', chat_id=1):
        monkeypatch.setattr(cache_module, 'ses', setup_and_teardown)
        cache = CacheDB()
        message = mock_message(text, chat_id)
        decorator = cache.set_cache(mock_func)
        decorator(message)
        assert cache.get_context(chat_id) == 'history of system response:\n' + text
