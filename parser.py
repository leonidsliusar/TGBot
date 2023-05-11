import os
from http.cookies import SimpleCookie
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from config import SQL_URL_MAIN, SQL_URL_QUESTIONS, USER_AGENT, DB_SCHEMAS_PATH, SQL_SCHEMA_LINK

load_dotenv()
username = os.getenv('USERNAME_SQL')
password = os.getenv('PASSWORD')
url = SQL_URL_MAIN
url_questions = SQL_URL_QUESTIONS
user_agent = USER_AGENT
db_schema_path = DB_SCHEMAS_PATH
db_schema_link = SQL_SCHEMA_LINK


class Parser:

    @staticmethod
    async def get_login(session: ClientSession) -> SimpleCookie[str]:  # logs in question's base
        payload = {
            'login': username,
            'psw': password
        }
        header = {
            'user-agent': user_agent
        }
        async with session.post(url, data=payload, headers=header) as client:
            cookies = client.cookies
            return cookies

    @property
    async def get_list_exercises(self) -> str:  # return a string with all questions
        async with ClientSession() as session:
            cookies = await self.get_login(session)
            async with session.get(url_questions, cookies=cookies) as response:
                page, status_code = await response.text(), response.status
        if str(status_code).startswith('5'):
            exercises = '5xx;'
        else:
            soup = BeautifulSoup(page, 'html.parser')
            pivot_tag = soup.find('select', {'id': 'LN'})
            tags = pivot_tag.find_all('option', {'value': lambda x: x.isnumeric()})
            exercises = ''
            for option in tags:
                exercises += str(option['value']) + ';'
        return exercises

    # return the question, schema and answer which chosen by user
    async def get_exercise(self, n: int) -> str | tuple[str, bytes | str, str]:
        async with ClientSession() as session:
            cookies = await self.get_login(session)
            async with session.get(f'{url_questions}&LN={n}', cookies=cookies) as response:
                response, status_code = await response.text(), response.status
        if str(status_code).startswith('5'):
            result = '5xx;'
            return result
        else:
            soup = BeautifulSoup(response, 'html.parser')
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
                scheme = db_schema_link
                res = description + '\n' + scheme + '\n' + question
            else:
                table_name = re.search(r'"(.+)"', description).group(1)
                with open(db_schema_path + table_name + '.png', 'rb') as pic:
                    scheme = pic.read()
                res = description + '\n\n' + question
            return res, scheme, answer


parser = Parser()
