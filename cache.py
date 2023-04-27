from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Any, Dict


class Cache(ABC):
    __slots__ = ['cache']

    @abstractmethod
    def set_cache(self, *args) -> Optional[Any]:
        pass

    @abstractmethod
    def get_context(self, *args) -> Optional[Any]:
        pass


class CacheMem(Cache):

    def __init__(self) -> None:
        self.cache: List[str] = []

    @property
    def get_context(self) -> str:
        if self.cache:
            res = '===CONTEXT START===' + ';'.join(self.cache) + '===CONTEXT END==='
        else:
            res = ''
        return res

    def set_cache(self, func: Callable[[str], str]) -> Callable[[str], str]:
        def wrapper(message: str) -> str:
            res = func(message)
            if res:
                self.cache.append(res)
            return res

        return wrapper


class CacheQuiz(Cache):

    def __init__(self) -> None:
        self.cache: Dict[int, str] = {}

    def set_cache(self, chat_id: int, answer: str) -> None:
        self.cache[chat_id] = answer

    def get_context(self, chat_id: int) -> str:
        return self.cache.get(chat_id, 0)


class CacheControl:
    @staticmethod
    def new_cache(type: str) -> Cache:
        if type == 'mem':
            cache = CacheMem()
        elif type == 'quiz':
            cache = CacheQuiz()
        return cache


memcache = CacheControl.new_cache('mem')
quiz_cache = CacheControl.new_cache('quiz')
