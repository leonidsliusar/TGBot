import os
import requests as requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from config import SQL_URL_MAIN, SQL_URL_QUESTIONS, USER_AGENT, DB_SCHEMAS_PATH

load_dotenv()
username = os.getenv('USERNAME_SQL')
password = os.getenv('PASSWORD')
url = SQL_URL_MAIN
url_questions = SQL_URL_QUESTIONS
user_agent = USER_AGENT
session = requests.Session()
db_schema_path = DB_SCHEMAS_PATH


def get_login() -> None:  # login to question's base
    payload = {
        'login': username,
        'psw': password
    }
    header = {
        'user-agent': user_agent
    }
    session.post(url, data=payload, headers=header)


def get_list_exercises() -> str:  # return a string with all questions
    response = session.get(url_questions)
    if str(response.status_code).startswith('5'):
        res = '5xx;'
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        pivot_tag = soup.find('select', {'id': 'LN'})
        tags = pivot_tag.find_all('option', {'value': lambda x: x.isnumeric()})
        res = ''
        for option in tags:
            res += str(option['value']) + ';'
    return res


def get_exercise(n: int) -> tuple[str, bytes | str, str]:  # return the question, schema and answer which chose by user
    response = session.get(url_questions + f'&LN={n}')
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('td', {'colspan': '2'})
    table.a.decompose()
    description = table.get_text('\n', strip=True)
    questions_table = soup.find('td', {'rowspan': '2'})
    questions_table.center.decompose()
    questions_table.div.decompose()
    questions_table.div.decompose()
    questions_table.div.decompose()
    question = questions_table.get_text('\n', strip=True)
    answer = soup.find('textarea').get_text(strip=True)
    if __name__ == '__main__':
        scheme = f'https://www.sql-ex.ru/help/select13.php?Lang=1#'
        res = description + '\n' + scheme + '\n' + question
    else:
        table_name = re.search(r'"(.+)"', description).group(1)
        with open(db_schema_path + table_name + '.png', 'rb') as pic:
            scheme = pic.read()
        res = description + '\n\n' + question
    return res, scheme, answer


if __name__ == '__main__':
    get_login()
    result, schema_, answer_ = get_exercise(50)
    print(result, schema_, answer_)
