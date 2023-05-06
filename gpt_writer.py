import io
import re
import time
from docx import Document
import requests
from dotenv import load_dotenv
import os
import openai
from openai.error import RateLimitError

from cache_module import db_cache
from logging_config import logger
from config import SYMBOLS_LENGTH_IN_BOOK


load_dotenv()
openai.api_key = os.getenv('API_GPT')
openai.organization = os.getenv('ORGANIZATION')
default_symbol_length = SYMBOLS_LENGTH_IN_BOOK


def chat_request(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role': 'user', 'content': message},
                  {'role': 'system', 'content': 'You are writer'}],
        temperature=1.2,
        max_tokens=1500,
        stop=None,
        frequency_penalty=1,
        presence_penalty=1,
    )
    return response


@db_cache.set_cache
def chat_response_writer(message):  # sending request to AI, return only one page and caching it in DB
    response = chat_request(message.text)
    page = response.choices[0]['message']['content']
    return page


def send_to_writer(message):  # sending request to continue the storyline
    symbol_length = re.search('\d+', message.text)
    pattern = re.compile('(\d+|symbols|/)')
    message_text = pattern.sub('', message.text)
    message_content = re.sub(' +', ' ', message_text)
    book_size = int(symbol_length.group(0)) if symbol_length else default_symbol_length
    length_book = len(db_cache.get_context(message.chat.id, render_book=True))
    while length_book < book_size:
        if length_book == 0:
            logger.debug(f'Book length: {length_book}')
            message.text = message_content
        else:
            chunk = db_cache.get_context(chat_id=message.chat.id, last_message_only=True)
            message.text = 'Continue the story in the same style: ' + chunk
        try:
            chat_response_writer(message)
            logger.debug(message.text)
        except RateLimitError:
            time.sleep(30)
            chat_response_writer(message)
        length_book = len(db_cache.get_context(message.chat.id, render_book=True))
    return


def render_book(message):  # rendering the book
    send_to_writer(message)
    book = db_cache.get_context(message.chat.id, render_book=True)
    db_cache.flush_context(message.chat.id)
    return book


def get_book(message):  # send request to rendering book and return doc file as bytestring in buffer
    book_string = render_book(message)
    logger.debug(book_string)
    book = Document()
    book.add_paragraph(book_string)
    buffer = io.BytesIO()
    book.save(buffer)
    buffer.seek(0)
    return buffer


def model_list(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get('https://api.openai.com/v1/engines', headers=headers)
    print(response.text)


if __name__ == '__main__':
    model_list(openai.api_key)
