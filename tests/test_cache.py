import pytest
from cache_module import cache, CacheMem, quiz_cache


class MockObjChat:
    def __init__(self, chat_id):
        self.id = chat_id


class MockMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = MockObjChat(chat_id)


@cache.set_cache
def func(message):
    return message.text


class TestCacheMem:

    @pytest.mark.parametrize('text1, text2, text3, chat_id',
                             [
                                 ('test1 test1 tests 1', 'tests 2 test2 test2', 'tests 3 test3', 1),
                             ])
    def test_memcache(self, text1, text2, text3, chat_id):

        assert cache.get_context(chat_id) == ''
        func(MockMessage(text1, chat_id))
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1
        func(MockMessage(text2, chat_id))
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1 + ';' + text2
        func(MockMessage(text3, chat_id))
        assert cache.get_context(chat_id) == 'history of system response:\n' + text1 + ';' + text2 + ';' + text3

    @pytest.mark.parametrize('capacity, chat_id',[(1, 'test0'), (70, 'test1'), (50, 'test2')])
    def test_cache_capacity(self, capacity, monkeypatch, chat_id):
        monkeypatch.setattr(CacheMem, '_MAX_CAPACITY', capacity)
        result_string = 'history of system response:\n'
        cache_list = []
        for n in range(60):
            func(MockMessage(str(n), chat_id))
            cache_list.append(str(n))
        if capacity < n:
            result_string += ";".join(cache_list[n - capacity:])
        else:
            result_string += ";".join(cache_list)
        assert cache.get_context(chat_id) == result_string

    @pytest.mark.xfail(raises=AttributeError)
    @pytest.mark.parametrize('capacity', [-5, 1.5, 'tests'])
    def test_constraint_memcache(self, capacity, monkeypatch):
        monkeypatch.setattr(CacheMem, '_MAX_CAPACITY', capacity)
        pass


class TestCacheQuiz:
    @pytest.mark.parametrize('chat_id, answer', [(-520.567, 'HelloTest32'), ('dwd', 123)])
    def test_set_cache_and_get_context(self, chat_id, answer):
        quiz_cache.set_cache(chat_id, answer)
        assert quiz_cache.get_context(chat_id) == answer
