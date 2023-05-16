import asyncio

import pytest

import cache_module
import log_config
import main
from main import greetings


class MockMessage:
    def __init__(self, chat_id, text):
        self.chat = MockChat(chat_id)
        self.text = text


class MockChat:
    def __init__(self, chat_id):
        self.id = chat_id


class MockBot:
    def send_message(self, chat_id, text):
        return text


@pytest.mark.skip
@pytest.mark.parametrize('message_id, text', [
    (123, 'test'),
])
async def test_instruction(message_id, text, monkeypatch):
    monkeypatch.setattr(cache_module, 'logger', logging_config.logger_test)
    monkeypatch.setattr(main, 'logger', logging_config.logger_test)
    monkeypatch.setattr(main, 'bot', MockBot())
    message = MockMessage(message_id, text)
    response = yield greetings(message)
    assert response == text
