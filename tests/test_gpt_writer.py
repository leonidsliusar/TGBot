import pytest

import cache_module
from gpt_writer import get_book, render_book
import gpt_writer


@cache_module.db_cache.set_cache
def mock_chat_response_writer(message):
    mock_response = 'response'
    return mock_response

@pytest.mark.skip
def test_render_book_1_page(monkeypatch, setup_and_teardown_db, mock_message, text1='10 first_test', text2='test2', chat_id=1):
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(gpt_writer, 'chat_response_writer', mock_chat_response_writer)
    message = mock_message(text1, chat_id)
    result = render_book(message)
    print(result)
    assert result == text1


def test_render_book_several_pages(monkeypatch, setup_and_teardown_db, mock_message, text1='40 first_test test', text2='test2', chat_id=1):
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(gpt_writer, 'chat_response_writer', mock_chat_response_writer)
    message = mock_message(text1, chat_id)
    result = render_book(message)
    print(result)
    assert result == 'responseresponseresponseresponseresponse'
