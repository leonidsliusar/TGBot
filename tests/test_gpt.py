import re
import pytest
import cache_module
import gpt
import logging_config
from gpt import GPTWriter, GPTFactoryWriter


@pytest.mark.asyncio
async def test_render_book(monkeypatch, event_loop, mock_chat_response_writer, setup_and_teardown_db, mock_message,
                           text1='10 first_test', text2='100test2', chat_id=1):
    monkeypatch.setattr(cache_module, 'logger', logging_config.logger_test)
    monkeypatch.setattr(gpt, 'logger', logging_config.logger_test)
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(GPTWriter, 'chat_response_writer', mock_chat_response_writer)
    message1 = mock_message(text1, chat_id)
    pattern = re.compile('\\d+|\\s')
    test_string1 = pattern.sub("", text1)
    expected_result = f'{test_string1}'
    result = await GPTFactoryWriter.get_gpt().render_book(message1)
    logging_config.logger_test.debug(f'Rendered page {result}')
    assert result == expected_result
    message2 = mock_message(text2, chat_id)
    test_string2 = pattern.sub("", text2)
    expected_result = ';'.join([test_string2]*21)
    result = await GPTFactoryWriter.get_gpt().render_book(message2)
    assert result == expected_result


@pytest.mark.asyncio
async def test_rewrite_text(monkeypatch, mock_chat_request_writer, event_loop, setup_and_teardown_db,
                            mock_message, text='test', chat_id=1):
    monkeypatch.setattr(cache_module, 'logger', logging_config.logger_test)
    monkeypatch.setattr(gpt, 'logger', logging_config.logger_test)
    monkeypatch.setattr(cache_module, 'ses', setup_and_teardown_db)
    monkeypatch.setattr(GPTWriter, 'chat_request', mock_chat_request_writer)
    message = mock_message(text, chat_id)
    result = await GPTFactoryWriter.get_gpt().rewrite_text(message)
    assert result.choices[0]['message']['content'] == 'stub response from stub chat'


