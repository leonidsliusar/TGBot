from typing import Type

from dotenv import load_dotenv
import os
import openai

from cache import memcache

load_dotenv()
openai.api_key = os.getenv('API_GPT')
openai.organization = os.getenv('ORGANIZATION')


def chat_request(message: str):
    request = str(memcache.get_context) + message
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=request,
        temperature=0.5,
        max_tokens=250,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0
    )
    return response


@memcache.set_cache
def chat_response(message: str):
    response = chat_request(message)
    deserialized_response = response.choices[0]['text']
    return deserialized_response
