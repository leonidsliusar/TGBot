from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, List, Callable, Any, Dict, Type
from sqlalchemy.orm import Session
from db import engine, Chat, Messages


class Cache(ABC):
    __slots__ = ['cache']

    @abstractmethod
    def set_cache(self, *args) -> Optional[Any]:
        pass

    @abstractmethod
    def get_context(self, *args) -> Optional[Any]:
        pass


class CacheMem(Cache):
    _MAX_CAPACITY: int = 50

    def __new__(cls, *args, **kwargs):
        if type(cls._MAX_CAPACITY) == int and cls._MAX_CAPACITY > 0:
            return super().__new__(cls)
        else:
            raise AttributeError

    def __init__(self) -> None:
        self.cache: Dict[int, List] = {}

    def get_context(self, chat_id) -> str:
        if self.cache.get(chat_id):
            context_list = list(self.cache[chat_id])
            res = 'history of system response:\n' + ';'.join(context_list)
        else:
            res = ''
        return res

    def set_cache(self, func: Callable[[Type[Messages]], str]) -> Callable[[Type[Messages]], str]:
        def wrapper(message) -> str:
            res = func(message)
            if res:
                if self.cache.get(message.chat.id, 0) == 0:
                    self.cache[message.chat.id] = deque()
                if len(self.cache[message.chat.id]) > self._MAX_CAPACITY:
                    self.cache[message.chat.id].popleft()
                self.cache[message.chat.id].append(res)
            return res

        return wrapper


class CacheQuiz(Cache):

    def __init__(self) -> None:
        self.cache: Dict[int, str] = {}

    def set_cache(self, chat_id: int, answer: str) -> None:
        self.cache[chat_id] = answer

    def get_context(self, chat_id: int) -> str:
        return self.cache.get(chat_id, 0)


class CacheDB(Cache):

    def set_cache(self, func: Callable[[Type[Messages]], str]) -> Callable[[Type[Messages]], str]:
        def wrapper(message):
            res = func(message)
            if res:
                chat_id = message.chat.id
                message = res
                with Session(engine) as session:
                    if session.query(Chat).filter(chat_id == chat_id).exists().scalar():
                        new_message = Messages(
                            chat_id=chat_id,
                            message=message
                        )
                        try:
                            session.add(new_message)
                        except:
                            session.rollback()
                            raise ConnectionError
                        else:
                            session.commit()
                    else:
                        new_chat = Chat(
                            chat_id=chat_id,
                            messages=message
                        )
                        new_message = Messages(
                            chat_id=chat_id,
                            message=message
                        )
                        try:
                            session.add(new_chat, new_message)
                        except:
                            session.rollback()
                            raise ConnectionError
                        else:
                            session.commit()
        return wrapper

    def get_context(self, chat_id) -> str:
        chat_id = chat_id
        with Session(engine) as session:
            res = ''
            if session.query(Chat.query.filter(chat_id == chat_id).exists()).scalar():
                query = session.query(Messages.message).filter_by(chat_id=chat_id)
                messages = session.execute(query)
                messages_string = ''
                for message in messages:
                    messages_string += message['massege'] + ';'
                res = 'history of system response:\n' + messages_string
            return res


class CacheControl:
    @staticmethod
    def new_cache(type: str) -> Cache:
        if type == 'mem':
            cache = CacheMem()
        elif type == 'quiz':
            cache = CacheQuiz()
        elif type == 'db':
            cache = CacheDB()
        return cache


# Config
cache = CacheControl.new_cache('db')
quiz_cache = CacheControl.new_cache('quiz')
