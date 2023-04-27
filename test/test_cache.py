import pytest
from cache import memcache


class TestCacheMem:

    @pytest.mark.parametrize('message1, message2, message3',
                             [
                                 ('test1 test1 test 1', 'test 2 test2 test2', 'test 3 test3'),
                             ])
    def test_memcache_get_context(self, message1, message2, message3):
        @memcache.set_cache
        def func(message):
            return message

        assert memcache.get_context == ''
        func(message1)
        assert memcache.get_context == '===CONTEXT START===' + message1 + '===CONTEXT END==='
        func(message2)
        assert memcache.get_context == '===CONTEXT START===' + message1 + ';' + message2 + '===CONTEXT END==='
        func(message3)
        assert memcache.get_context == '===CONTEXT START===' + message1 + ';' + message2 + ';' + message3 + \
               '===CONTEXT END==='
