import random

import pytest
import parser
from parser import get_login, get_exercise, get_list_exercises


class TestParser:

    @pytest.mark.parametrize('test_url, test_username, test_password, test_user_agent', [
                            ('test_url', 'useruser', 'qwerty123456', 'Python'),
                            (123, 123, 123, 456)
    ])
    def test_get_login_send_post(self, test_url, test_username, test_password,
                                 test_user_agent, monkeypatch, set_session):
        session = set_session('pass')
        monkeypatch.setattr(parser, 'session', session)
        monkeypatch.setattr(parser, 'url', test_url)
        monkeypatch.setattr(parser, 'username', test_username)
        monkeypatch.setattr(parser, 'password', test_password)
        monkeypatch.setattr(parser, 'user_agent', test_user_agent)
        get_login()
        assert session.url == test_url
        assert session.data == {'login': test_username, 'psw': test_password}
        assert session.headers == {'user-agent': test_user_agent}

    @pytest.mark.parametrize('test_url, expected_result', [
                            ('Server Error', '5xx'),
                            ('some_url', 'tests')
    ])
    def test_get_list_exercises(self, tmp_path, test_url, get_instance_mock_beauty_soup,
                                expected_result, monkeypatch, set_session):
        session = set_session(expected_result)
        monkeypatch.setattr(parser, 'session', session)
        monkeypatch.setattr(parser, 'url_questions', test_url)
        monkeypatch.setattr(parser, 'BeautifulSoup', get_instance_mock_beauty_soup)
        assert get_list_exercises() == expected_result + ';'
        temp_file = tmp_path / f'{expected_result}.png'
        temp_file.write_bytes(expected_result.encode())
        mock_path = tmp_path.absolute()
        monkeypatch.setattr(parser, 'db_schema_path', str(mock_path)+'/')
        assert get_exercise(random.randint(1, 100)) == ('\"'
                                                        + expected_result
                                                        + '\"\n\n\"'
                                                        + expected_result
                                                        + '\"', expected_result.encode(), '\"'
                                                        + expected_result
                                                        + '\"')
