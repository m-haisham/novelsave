import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, List, Any, Dict

from requests.cookies import RequestsCookieJar

from .exceptions import DuplicateCookieError


class CookieDatabase:
    name = 'Cookies'
    memory = 'file::memory:?cache=shared'

    def __init__(self, dir_path: Union[Path, str, None]):
        """
        :param dir_path: Different inputs lead to different cases
            :dir_path Path: connects to the file in the path provided, if file does not exist, creates the file
            :dir_path str: same as in Path if its a path, if its literal ':memory:' creates database in memory
            :dir_path None: creates the database in memory
        """
        # parameter validation
        if isinstance(dir_path, Path):  # May receive WindowsPath or PosixPath which are child classes of Path
            self.path = dir_path / self.name
        elif type(dir_path) == str:
            self.path = Path(dir_path) / self.name

        # connect to in memory database
        if dir_path is None or dir_path == ':memory:':
            self.conn = sqlite3.connect(self.memory, uri=True)

        # type check, path was defined
        elif hasattr(self, 'path'):
            self.conn = sqlite3.connect(str(self.path))

        # dir_path was not of any accepted value
        else:
            raise TypeError(f"'dir_path' of {dir_path} is not of any acceptable type or value. "
                            f"see function doc for more info.")

        self.cursor = self.conn.cursor()
        self._create_table()

    def select(self, domains: Union[tuple, str]) -> Tuple[Dict[str, Any]]:
        """
        Searches for the cookies in the given domains

        :param domains: domain targeted by cookie
        :return: cookies in dict form
        """
        # parameter validation
        if type(domains) == str:
            domains = (domains, )

        # build statement
        statement = 'SELECT * FROM cookies' + self._build_domain_condition(domains)

        # execute select query
        with self.conn:
            self.cursor.execute(statement, domains)

        # map values to their fields
        cookies = []
        for row in self.cursor.fetchall():
            cookies.append(self._parse_row(row))

        return tuple(cookies)

    def insert(self, cookies: Union[List[Tuple[str, str, str, str, int]], RequestsCookieJar]) -> None:
        """
        Adds the given cookies to database

        :warning: if exception is thrown, no data is added
        """
        # parameter validation
        if type(cookies) == RequestsCookieJar:
            # extract needed values
            values = []
            for c in cookies:
                values.append((c.name, c.value, c.domain, c.path, c.expires,))

        elif type(cookies) == list:
            values = cookies

        else:
            raise TypeError(f'Unsupported type: {type(cookies[0])} (tuple, http.cookiejar.Cookie)')

        # execute insert query
        try:
            with self.conn:
                self.cursor.executemany("INSERT INTO cookies VALUES(?, ?, ?, ?, ?)", values)
        except sqlite3.IntegrityError as e:
            if str(e).startswith('UNIQUE constraint failed'):
                raise DuplicateCookieError(str(e))
            else:
                raise e

    def delete(self, domains: Union[str, tuple]) -> None:
        """
        Removes the cookies with the provided domains

        :param domains: domain targeted by cookie
        :raises ValueError: if domains are empty or is null
        """
        # parameter check
        if not bool(domains):
            raise ValueError("'domains' must not be empty or null")
        elif type(domains) == str:
            domains = (domains, )

        # build statement
        statement = 'DELETE FROM cookies' + self._build_domain_condition(domains)

        # execute delete statement
        with self.conn:
            self.cursor.execute(statement, domains)

    def all(self) -> Tuple[Dict[str, Any]]:
        """
        :return: All cookies in the database
        """
        # execute select query
        with self.conn:
            self.cursor.execute('SELECT * FROM cookies')

        # map values to their fields
        return self._parse_result_set()

    def close(self):
        """
        Closes database connection
        """
        self.conn.close()

    def _create_table(self):
        with self.conn:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cookies(
                    name TEXT NOT NULL,
                    value TEXT,
                    domain TEXT NOT NULL,
                    path TEXT,
                    expires INTEGER,
                    PRIMARY KEY(name, domain)
                );
            """)

    def check_expired(self, cookies: Tuple[dict]):
        """
        :param cookies: cookies list to test
        :return: whether any of the cookies provided are expired
        """
        now = datetime.now()
        for cookie in cookies:
            expire_time = datetime.fromtimestamp(cookie['expires'])
            if expire_time < now:
                return True

        return False

    def _parse_row(self, row) -> Dict[str, Any]:
        return {
            'name': row[0],
            'value': row[1],
            'domain': row[2],
            'path': row[3],
            'expires': int(row[4]),
        }

    def _parse_result_set(self) -> Tuple[Dict[str, Any]]:
        """
        :return: parsed cookies from current cursor result set
        """
        cookies = []
        for row in self.cursor.fetchall():
            cookies.append(self._parse_row(row))

        return tuple(cookies)

    def _build_domain_condition(self, domains: Union[List[str], Tuple[str]], join: str = 'OR') -> str:
        postfix = ''
        if domains:
            postfix += " WHERE domain=?"
            postfix += f" {join} domain=?" * (len(domains) - 1)

        return postfix

