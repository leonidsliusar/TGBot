import asyncio
import random
import re
import time

import aiohttp
from aiogram.types import InputFile
from cache_module import quiz_cache
from aiogram import Bot, Dispatcher, executor, types, filters
from dotenv import load_dotenv
import os
from gpt import GPTFactoryAssistant, GPTFactoryWriter
import parser as sql
from config import SYMBOLS_LENGTH_IN_BOOK as book_size
from logging_config import logger_main

load_dotenv()
API_TOKEN = os.getenv('API_TELEGRAM')
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
assistant = GPTFactoryAssistant.get_gpt()
writer = GPTFactoryWriter.get_gpt()
logger = logger_main


@dp.message_handler(commands=['help'])
async def greetings(message: types.Message):
    response = 'I accept to recognize native text.\nI can speak in big range of languages.' \
               'You can just try it by typing something.' \
               '\n\nI am able to write a book for you. You can learn more about this feature by text me /hwrite' \
               '\n\nI also got some SQL-quiz. You can find out more by typing /hsql'
    await bot.send_message(chat_id=message.chat.id, text=response)


@dp.message_handler(commands=['sql'])
async def show_exercises(message: types.Message):
    sql.get_login()
    list_of_questions = sql.get_list_exercises()
    if list_of_questions == '5xx':
        response = 'Server with questions is dead. Try later please'
    else:
        last_question = quiz_cache.get_context(message.chat.id)
        response = 'I got really grand range of SQL questions\n'
        for question in list_of_questions.split(';'):
            response += f'/e{question} '
        response += f'\nThe last question was {str(last_question[0])}' if last_question != 0 \
            else ''
    await message.reply(response)


@dp.message_handler(commands=['hsql'])
async def tell_me_more(message: types.Message):
    last_question = quiz_cache.get_context(message.chat.id)
    remainder_string = f'\nThe last question was {str(last_question[0])}' if last_question != 0 \
        else f'\nYou didn\'t give me answer yet'
    response = 'I got some SQL-exercises. It\'s kinda quiz with a big range of different SQL query questions.' \
               '\nYou can try it for free. Just send me /sql' \
               '\nYou can take the right answer by sending me /sql_answer' \
               f'{remainder_string}'
    await message.reply(response)


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=['e([\\d]{1,3})']))
async def get_exercise(message: types.Message):
    n = int(re.findall(r'\d', message.text)[0])
    question, schema, answer = sql.get_exercise(n)
    chat_id = message.chat.id
    quiz_cache.set_cache(chat_id, str(n) + answer)
    await message.reply(question)
    await bot.send_photo(chat_id=chat_id, photo=schema)


@dp.message_handler(regexp=re.compile(r'.*(thank you|thank\'s).*', re.IGNORECASE))
async def send_emoji(message: types.Message):
    choices_list = ['💞', '❤️', '🔥', '🤝']
    emoji = random.choice(choices_list)
    await message.reply(emoji)


@dp.message_handler(filters.Text(startswith=['SELECT', 'select', 'Select']))
async def check_answer(message: types.Message):
    chat_id = message.chat.id
    correct_answer = quiz_cache.get_context(chat_id)[1:]
    user_answer = message.text
    if user_answer.strip(" ").lower() == correct_answer.strip(" ").lower() \
            and user_answer.strip(" ").upper() == correct_answer.strip(" ").upper():
        await bot.send_message(chat_id=chat_id, text='That\'s it')
        await show_exercises(message)
    else:
        await bot.send_message(chat_id=chat_id, text='Alas, wrong')


@dp.message_handler(commands=['sql_answer'])
async def give_answer(message: types.Message):
    chat_id = message.chat.id
    try:
        correct_answer = quiz_cache.get_context(chat_id)[1:]
    except TypeError:
        correct_answer = 'You didn\'t take any question yet'
    await bot.send_message(chat_id=chat_id, text=correct_answer)


@dp.message_handler(commands=['hwrite'])
async def tell_me_more(message: types.Message):
    response = 'It is possible if I write book for you.' \
               'You can try it for free.\nJust send me description what exactly you want and ' \
               'mark it at the start with /write tag. ' \
               '\nAlso you can add in description size of book in symbols adding a numeric value.' \
               f'\nIf you aren\'t using numeric, it will produce book in default size {book_size} symbols.' \
               '\n<b>But if you are using numeric in query be sure that first numeric it\'s size of book!</b>' \
               '\n\n✅<b>Correct example for book with 5000 symbols:' \
               '\n/write 5000 a horror book about lost in forest in Steven King\'s style' \
               '\n\n✅Correct example for book with 100 symbols:' \
               '\n/write a short story about animals in 100 symbols\'s</b>' \
               '\n\n❌<b>Incorrect example. It won\'t work properly cause /tag order was broken:' \
               '\n5000/write a book about smoking is bad' \
               '\n\n❌Incorrect example. It write exactly one book with 11 symbols:' \
               '\n/write 11 book. One book - 500 symbols</b>'
    await message.reply(response, parse_mode='HTML')


@dp.message_handler(commands=['write'])
async def gpt_writer(message: types.Message):
    try:
        buffer = await writer.get_book(message)
        if not buffer:
            response_from_chat = 'Sorry I didn\'t catch the words. Can you tell me more detail'
            await message.reply(response_from_chat)
        buffer.seek(0)
        book = InputFile(buffer, filename='new_book.docx')
        await bot.send_document(chat_id=message.chat.id, document=book, caption='Your new book')
    except Exception as e:
        logger.error(e)
        await bot.send_message(chat_id=message.chat.id, text='Server is down. Try later')


@dp.message_handler()
async def chat_gpt(message: types.Message):
    response_from_chat = await assistant.chat_response(message)
    if not response_from_chat:
        response_from_chat = 'Sorry I didn\'t catch the words'
    await message.reply(response_from_chat)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
