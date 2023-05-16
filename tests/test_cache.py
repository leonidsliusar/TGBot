import pytest
import log_config
from cache_module import CacheMem, CacheDB, quiz_cache
import cache_module
from gpt import GPTFactoryAssistant


class TestCacheMem:
    instance = GPTFactoryAssistant.get_gpt()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('text1, text2, text3, chat_id',
                             [
                                 ('test1 test1 tests 1', 'tests 2 test2 test2', 'tests 3 test3', 1)
                             ])
    async def test_memcache(self, mock_coroutine, event_loop, mock_message, text1, text2, text3, chat_id):
        cache = CacheMem()
        message1 = mock_message(text1, chat_id)
        message2 = mock_message(text2, chat_id)
        message3 = mock_message(text3, chat_id)
        decorator = cache.set_cache(mock_coroutine)
        await decorator(cache, message1)
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1
        await decorator(cache, message2)
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1 + ';' + text2
        await decorator(cache, message3)
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1 + ';' + text2 + ';' + text3

    @pytest.mark.asyncio
    @pytest.mark.parametrize('capacity, chat_id', [(1, 'test0'), (70, 'test1'), (50, 'test2')])
    async def test_cache_capacity(self, capacity, monkeypatch, mock_coroutine, mock_message, chat_id):
        monkeypatch.setattr(CacheMem, '_MAX_CAPACITY', capacity)
        result_string = 'history of system response:\n'
        cache_list = []
        cache = CacheMem()
        for n in range(60):
            decorator = cache.set_cache(mock_coroutine)
            message = mock_message(str(n), chat_id)
            await decorator(cache, message)
            cache_list.append(str(n))
        if capacity < n:
            result_string += ";".join(cache_list[n - capacity:])
        else:
            result_string += ";".join(cache_list)
        assert cache.get_context(chat_id) == result_string

    @pytest.mark.xfail(raises=ValueError)
    @pytest.mark.parametrize('capacity', [-5, 1.5, 'tests'])
    def test_constraint_memcache(self, capacity, monkeypatch):
        monkeypatch.setattr(CacheMem, '_MAX_CAPACITY', capacity)
        pass


class TestCacheQuiz:
    @pytest.mark.parametrize('chat_id, answer', [(-520.567, 'HelloTest32'), ('dwd', 123)])
    def test_set_cache_and_get_context(self, chat_id, answer):
        quiz_cache.set_cache(chat_id, answer)
        assert quiz_cache.get_context(chat_id) == answer


class TestDB:
    instance = GPTFactoryAssistant.get_gpt()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('text_user_1_1, text_user_1_2, chat_id_user_1,'
                             'text_user_2_1, text_user_2_2, chat_id_user_2',
                             [
                                ('test_1_user_1', 'test_2_user_1', 1, 'test_1_user_2', 'test_2_user_2', 2)
                             ])
    async def test_set_get_cache(self, monkeypatch, setup_and_teardown_db, mock_coroutine, mock_message,
                           text_user_1_1, text_user_1_2, chat_id_user_1,
                           text_user_2_1, text_user_2_2, chat_id_user_2):
        monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
        cache = CacheDB()
        message_user_1_1 = mock_message(text_user_1_1, chat_id_user_1)
        message_user_1_2 = mock_message(text_user_1_2, chat_id_user_1)
        decorator = cache.set_cache(mock_coroutine)
        await decorator(cache, message_user_1_1)
        assert cache.get_context(chat_id_user_1) == 'history of system response:\n' + text_user_1_1
        await decorator(cache, message_user_1_2)
        assert cache.get_context(chat_id_user_1) == 'history of system response:\n' \
                                                    + text_user_1_1 + ';' + text_user_1_2
        message_user_2_1 = mock_message(text_user_2_1, chat_id_user_2)
        message_user_2_2 = mock_message(text_user_2_2, chat_id_user_2)
        await decorator(cache, message_user_2_1)
        assert cache.get_context(chat_id_user_2) == 'history of system response:\n' + text_user_2_1
        await decorator(cache, message_user_2_2)
        assert cache.get_context(chat_id_user_2) == 'history of system response:\n' \
                                                    + text_user_2_1 + ';' + text_user_2_2
        assert cache.get_context(chat_id_user_2, last_message_only=True) == text_user_2_2

    @pytest.mark.asyncio
    @pytest.mark.parametrize('text_user_1_1, text_user_1_2, chat_id_user_1,'
                             ' text_user_2_1, text_user_2_2, chat_id_user_2',
                             [
                                (None, 11, 1, 123456, True, 2)
                             ])
    async def test_set_get_cache_message_not_string(self, monkeypatch, setup_and_teardown_db, mock_coroutine, mock_message,
                                              text_user_1_1, text_user_1_2, chat_id_user_1,
                                              text_user_2_1, text_user_2_2, chat_id_user_2):
        monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
        cache = CacheDB()
        message_user_1_1 = mock_message(text_user_1_1, chat_id_user_1)
        message_user_1_2 = mock_message(text_user_1_2, chat_id_user_1)
        decorator = cache.set_cache(mock_coroutine)
        await decorator(self.instance, message_user_1_1)
        assert cache.get_context(chat_id_user_1) == ''
        await decorator(self.instance, message_user_1_2)
        assert cache.get_context(chat_id_user_1) == ''
        message_user_2_1 = mock_message(text_user_2_1, chat_id_user_2)
        message_user_2_2 = mock_message(text_user_2_2, chat_id_user_2)
        await decorator(self.instance, message_user_2_1)
        assert cache.get_context(chat_id_user_2) == ''
        await decorator(self.instance, message_user_2_2)
        assert cache.get_context(chat_id_user_2) == ''
