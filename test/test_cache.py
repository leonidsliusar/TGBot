import pytest
from cache import memcache


class TestCacheMem:

    @pytest.mark.parametrize('text1, text2, text3, chat_id',
                             [
                                 ('test1 test1 test 1', 'test 2 test2 test2', 'test 3 test3', 1),
                             ])
    def test_memcache_get_context(self, text1, text2, text3, chat_id):
        class MockObjChat:
            def __init__(self, chat_id):
                self.id = chat_id

        class MockMessage:
            def __init__(self, text, chat_id):
                self.text = text
                self.chat = MockObjChat(chat_id)

        @memcache.set_cache
        def func(message):
            return message.text

        assert memcache.get_context(chat_id) == ''
        func(MockMessage(text1, chat_id))
        assert memcache.get_context(chat_id) == '===CONTEXT START===' + text1 + '===CONTEXT END==='
        func(MockMessage(text2, chat_id))
        assert memcache.get_context(chat_id) == '===CONTEXT START===' + text1 + ';' + text2 + '===CONTEXT END==='
        func(MockMessage(text3, chat_id))
        assert memcache.get_context(chat_id) == '===CONTEXT START===' + text1 + ';' + text2 + ';' + text3 + \
               '===CONTEXT END==='
