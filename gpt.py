import asyncio
from abc import ABC, abstractmethod
import requests
from dotenv import load_dotenv
import os
import openai
from openai.error import RateLimitError
import io
import re
import time
from docx import Document
from cache_module import memcache, db_cache
from config import SYMBOLS_LENGTH_IN_BOOK, TEXT_REWRITE_ITERATION


class GPT(ABC):
    load_dotenv()
    openai.api_key = os.getenv('API_GPT')
    openai.organization = os.getenv('ORGANIZATION')

    __slots__ = ['model_property', 'content']

    def __init__(self, model_property, content=None):
        self.model_property = model_property
        self.content = content

    async def chat_request(self, message):
        response = await openai.ChatCompletion.acreate(
            model=self.model_property['model'],
            messages=[{'role': 'user', 'content': message}, {'role': 'system', 'content': self.content}],
            temperature=self.model_property['temperature'],
            max_tokens=self.model_property['max_tokens'],
            stop=self.model_property['stop'],
            frequency_penalty=self.model_property['frequency_penalty'],
            presence_penalty=self.model_property['presence_penalty']
        )
        return response

    @staticmethod
    def model_list():
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
        }
        response = requests.get('https://api.openai.com/v1/engines', headers=headers)
        return response


class GPTAssistant(GPT):

    async def chat_request(self, message):
        self.content = memcache.get_context(message.chat.id)
        return await super().chat_request(message.text)

    @memcache.set_cache
    async def chat_response(self, message):
        response = await self.chat_request(message)
        deserialized_response = response.choices[0]['message']['content']
        return deserialized_response


class GPTWriter(GPT):
    default_symbol_length = SYMBOLS_LENGTH_IN_BOOK
    iteration_quantity = TEXT_REWRITE_ITERATION

    async def rewrite_text(self, message):  # repeat the request for write text to AI a few time to improve text quality
        response = await self.chat_request(message.text)
        n = 1
        while n != self.iteration_quantity:
            page_text = response.choices[0]['message']['content']
            try:
                response = await self.chat_request(
                    'Rewrite this text with more detail and fixing grammatical errors, but in the same style'
                    + page_text)
            except RateLimitError:
                time.sleep(40)
                response = await self.chat_request(
                    'Rewrite this text with more detail and fixing grammatical errors, but in the same style'
                    + page_text)
            n += 1
        return response

    @db_cache.set_cache
    async def chat_response_writer(self, message):  # sending request to AI, return only one page and caching it in DB
        response = await self.chat_request(message.text)
        page = response.choices[0]['message']['content']
        return page

    def parse_message(self, message):  # parse message to three variable and return it to send_to_writer func
        symbol_length = re.search('\\d+', message.text)
        pattern = re.compile('(\\d+|symbols|/)')
        message_text = pattern.sub('', message.text)
        message_content = re.sub(' +', ' ', message_text)
        book_size = int(symbol_length.group(0)) if symbol_length else self.default_symbol_length
        length_book = len(db_cache.get_context(message.chat.id, render_book=True))
        return book_size, message_content, length_book

    async def send_to_writer(self, message):  # sending request to continue the storyline until
        book_size, message_content, length_book = self.parse_message(message)
        while length_book < book_size:
            if length_book == 0:
                message.text = message_content
            else:
                chunk = db_cache.get_context(chat_id=message.chat.id, last_message_only=True)
                message.text = 'Continue the story in the same style: ' + chunk
            try:
                await self.chat_response_writer(message)
            except RateLimitError:
                await asyncio.sleep(30)
                await self.chat_response_writer(message)
            length_book = len(db_cache.get_context(message.chat.id, render_book=True))
        return

    async def render_book(self, message):  # rendering the book
        await self.send_to_writer(message)
        book = db_cache.get_context(message.chat.id, render_book=True)
        db_cache.flush_context(message.chat.id)
        return book

    async def get_book(self, message):  # send request to rendering book and return doc file as bytestring in buffer
        book_string = await self.render_book(message)
        book = Document()
        book.add_paragraph(book_string)
        buffer = io.BytesIO()
        book.save(buffer)
        buffer.seek(0)
        return buffer


class GPTFactory(ABC):

    @staticmethod
    @abstractmethod
    def get_gpt() -> GPT:
        pass


class GPTFactoryAssistant:

    @staticmethod
    def get_gpt() -> GPTAssistant:
        model_property = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.8,
            'max_tokens': 250,
            'stop': None,
            'frequency_penalty': 1,
            'presence_penalty': 1,
        }
        return GPTAssistant(model_property)


class GPTFactoryWriter:

    @staticmethod
    def get_gpt() -> GPTWriter:
        model_property = {
            'model': 'gpt-3.5-turbo',
            'temperature': 1.2,
            'max_tokens': 1500,
            'stop': None,
            'frequency_penalty': 1,
            'presence_penalty': 1,
        }
        content = 'You are writer'
        return GPTWriter(model_property, content)


if __name__ == "__main__":
    GPT.model_list()
