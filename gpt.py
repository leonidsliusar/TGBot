import json
from typing import Type

import requests
from dotenv import load_dotenv
import os
import openai

from cache import cache

load_dotenv()
openai.api_key = os.getenv('API_GPT')
openai.organization = os.getenv('ORGANIZATION')


def chat_request(message):
    chat_history = cache.get_context(message.chat.id)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role': 'user', 'content': f'{message.text}'}, {'role': 'system', 'content': f'{chat_history}'}],
        temperature=0.8,
        max_tokens=250,
        stop=None,
        frequency_penalty=1,
        presence_penalty=1
    )
    return response


@cache.set_cache
def chat_response(message):
    response = chat_request(message)
    deserialized_response = response.choices[0]['message']['content']
    return deserialized_response


def model_list(API_KEY):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
    }
    response = requests.get('https://api.openai.com/v1/engines', headers=headers)
    print(response.text)

if __name__ == '__main__':
    model_list(openai.api_key)