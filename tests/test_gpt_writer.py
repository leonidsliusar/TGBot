import re

import pytest
import cache_module
from gpt import GPTWriter, GPTFactoryWriter


@cache_module.db_cache.set_cache
def mock_chat_response_writer(instance, message):
    pattern = re.compile('(Continue the story in the same style:)|\\s')
    mock_response = pattern.sub("", message.text)
    return mock_response


def test_render_book_1_page(monkeypatch, setup_and_teardown_db, mock_message, text1='10 first_test', text2='test2', chat_id=1):
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(GPTWriter, 'chat_response_writer', mock_chat_response_writer)
    message = mock_message(text1, chat_id)
    pattern = re.compile('\\d+|\\s')
    test_string = pattern.sub("", text1)
    expected_result = f'{test_string}'
    result = GPTFactoryWriter.get_gpt().render_book(message)
    assert result == expected_result


def test_render_book_several_pages(monkeypatch, setup_and_teardown_db, mock_message, text1='40 first_test test', text2='test2', chat_id=1):
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(GPTWriter, 'chat_response_writer', mock_chat_response_writer)
    message = mock_message(text1, chat_id)
    result = GPTFactoryWriter.get_gpt().render_book(message)
    pattern = re.compile('\\d+|\\s')
    test_string = pattern.sub("", text1)
    expected_result = f'{test_string};{test_string};{test_string}'
    assert result == expected_result
