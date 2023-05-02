import pytest

from cache_module import CacheDB
import cache_module


class TestDB:
    @pytest.mark.parametrize('text_user_1_1, text_user_1_2, chat_id_user_1, text_user_2_1, text_user_2_2, chat_id_user_2',
    [
                            ('test_1_user_1', 'test_2_user_1', 1, 'test_1_user_2', 'test_2_user_2', 2)
    ])
    def test_set_get_cache(self, monkeypatch, setup_and_teardown_db, mock_func, mock_message,
                           text_user_1_1, text_user_1_2, chat_id_user_1,
                           text_user_2_1, text_user_2_2, chat_id_user_2):
        monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
        cache = CacheDB()
        message_user_1_1 = mock_message(text_user_1_1, chat_id_user_1)
        message_user_1_2 = mock_message(text_user_1_2, chat_id_user_1)
        decorator = cache.set_cache(mock_func)
        decorator(message_user_1_1)
        assert cache.get_context(chat_id_user_1) == 'history of system response:\n' + text_user_1_1
        decorator(message_user_1_2)
        assert cache.get_context(chat_id_user_1) == 'history of system response:\n' + text_user_1_1 + ';' + text_user_1_2
        message_user_2_1 = mock_message(text_user_2_1, chat_id_user_2)
        message_user_2_2 = mock_message(text_user_2_2, chat_id_user_2)
        decorator(message_user_2_1)
        assert cache.get_context(chat_id_user_2) == 'history of system response:\n' + text_user_2_1
        decorator(message_user_2_2)
        assert cache.get_context(chat_id_user_2) == 'history of system response:\n' + text_user_2_1 + ';' + text_user_2_2

    @pytest.mark.skip
    @pytest.mark.parametrize(
        'text_user_1_1, text_user_1_2, chat_id_user_1, text_user_2_1, text_user_2_2, chat_id_user_2',
        [
            ('test_1_user_1', True, 1, 123456, 'test_2_user_2', 2)
        ])
    def test_set_get_cache_message_not_string(self, monkeypatch, setup_and_teardown_db, mock_func, mock_message,
                           text_user_1_1, text_user_1_2, chat_id_user_1,
                           text_user_2_1, text_user_2_2, chat_id_user_2):
        monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
        cache = CacheDB()
        message_user_1_1 = mock_message(text_user_1_1, chat_id_user_1)
        message_user_1_2 = mock_message(text_user_1_2, chat_id_user_1)
        decorator = cache.set_cache(mock_func)
        decorator(message_user_1_1)
        assert cache.get_context(chat_id_user_1) == 'history of system response:\n' + text_user_1_1
        decorator(message_user_1_2)
        assert cache.get_context(
            chat_id_user_1) == 'history of system response:\n' + text_user_1_1
        message_user_2_1 = mock_message(text_user_2_1, chat_id_user_2)
        message_user_2_2 = mock_message(text_user_2_2, chat_id_user_2)
        decorator(message_user_2_1)
        assert cache.get_context(chat_id_user_2) == 'history of system response:\n'
        decorator(message_user_2_2)
        assert cache.get_context(
            chat_id_user_2) == 'history of system response:\n' + text_user_2_2