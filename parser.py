import os
import requests as requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

load_dotenv()
username = os.getenv('USERNAME_SQL')
password = os.getenv('PASSWORD')
url = 'https://sql-ex.ru/index.php'
url_questions = 'https://www.sql-ex.ru/exercises/index.php?act=learn'

session = requests.Session()


def get_login() -> None:
    payload = {
        'login': username,
        'psw': password
    }
    header = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'
    }
    session.post(url, data=payload, headers=header)


def get_list_exercises() -> list[str]:
    response = session.get(url_questions)
    if str(response.status_code).startswith('5'):
        res = '5xx'
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        pivot_tag = soup.find('select', {'id': 'LN'})
        tags = pivot_tag.find_all('option', {'value': lambda x: x.isnumeric()})
        res = []
        for option in tags:
            res.append(option['value'])
    return res


def get_exercise(n: int) -> tuple[str, bytes, str]:
    response = session.get(url_questions + f'&LN={n}')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('td', {'colspan': '2'})
    description = table.get_text('\n', strip=True)
    questions_table = soup.find('td', {'rowspan': '2'})
    questions_table.center.decompose()
    questions_table.div.decompose()
    questions_table.div.decompose()
    questions_table.div.decompose()
    question = questions_table.get_text('\n', strip=True)
    answer = soup.find('textarea').get_text(strip=True)
    if __name__ == '__main__':
        attachment = 'https://www.sql-ex.ru/help/select13.php?Lang=1#'
        res = description + '\n' + attachment + '\n' + question
    else:
        table_name = re.search(r'"(.+)"', description).group(1)
        with open(f'db_scheme/{table_name}.png', 'rb') as pic:
            scheme = pic.read()
        res = description + '\n' + question
    return res, scheme, answer




#get_login()
#res, schema, answer = get_exercise(1)

