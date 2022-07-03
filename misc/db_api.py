import datetime
import sqlite3
from dataclasses import dataclass
from typing import Union

# нэминг полей
TABLE_USERS_NAME = 'Users'
IDENTIFIER_LINE_NAME = 'id'
MEMBERSHIP_LINE_NAME = 'member_end'
S_DAY_LIMIT = 's_day_end'
ONE_ADVERT_LINE_NAME = 'one_advert'


@dataclass
class DB:

    def __init__(self, path_db='users.db'):
        self.path_db = path_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_db)

    def execute(self, command: str, params: tuple = (), fetch_one=False, fetch_all=False, commit=False) -> Union[
        tuple, list[tuple]]:

        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(command, params)

        data = None

        if commit:
            connection.commit()
        if fetch_one:
            data = cursor.fetchone()
        if fetch_all:
            data = cursor.fetchall()

        connection.close()

        return data

    def create_table_users(self):
        command = f'''
        CREATE TABLE IF NOT EXISTS {TABLE_USERS_NAME}(
        {IDENTIFIER_LINE_NAME} int PRIMARY KEY,
        {MEMBERSHIP_LINE_NAME} TIMESTAMP NOT NULL,
        {S_DAY_LIMIT} int NOT NULL,
        {ONE_ADVERT_LINE_NAME} int NOT NULL);
        '''

        self.execute(command, commit=True)



    def add_user(self, identifier: int, m_day_end: str='', s_day_end: str= '', one: int=0):
        command = f'''
        INSERT INTO {TABLE_USERS_NAME} VALUES(?, ?, ?, ?)
        '''

        self.execute(command, (identifier, m_day_end, s_day_end, one), commit=True)

    def is_exist_user(self, identifier: int) -> bool:
        command = f'''
                SELECT {IDENTIFIER_LINE_NAME} FROM {TABLE_USERS_NAME} WHERE {IDENTIFIER_LINE_NAME} = ?
                        '''
        f = self.execute(command, (identifier,), fetch_one=True)

        return bool(f)



    def update_s_day(self, indentifier: int, s_day: int):
        """

        :param indentifier:
        :param s_day: timestamp
        :return:
        """
        command = f'''
                UPDATE {TABLE_USERS_NAME} SET {S_DAY_LIMIT} = ? WHERE {IDENTIFIER_LINE_NAME} = ? 
                '''
        self.execute(command, (s_day, indentifier,), commit=True)

    def update_m_day(self, indentifier: int, m_day: str):
        command = f'''
                  UPDATE {TABLE_USERS_NAME} SET {MEMBERSHIP_LINE_NAME} = ? WHERE {IDENTIFIER_LINE_NAME} = ? 
                  '''
        self.execute(command, (m_day, indentifier,), commit=True)

    def get_one_of_user(self, identifier: int) -> int:
        command = f'''
                SELECT {ONE_ADVERT_LINE_NAME} FROM {TABLE_USERS_NAME} WHERE {IDENTIFIER_LINE_NAME} = ?
                        '''
        f = self.execute(command, (identifier,), fetch_one=True)[0]

        return f



    def update_one(self, indentifier: int, one: int):
        command = f'''
                  UPDATE {TABLE_USERS_NAME} SET {ONE_ADVERT_LINE_NAME} = ? WHERE {IDENTIFIER_LINE_NAME} = ? 
                  '''
        current = self.get_one_of_user(indentifier)

        self.execute(command, (current + one, indentifier,), commit=True)


    def get_users(self) -> list[tuple]:
        command = f'''
                SELECT * FROM {TABLE_USERS_NAME}
                        '''
        f = self.execute(command, (), fetch_all=True)

        return f

    def get_user(self, identifier: int) -> tuple:
        command = f'''
                SELECT * FROM {TABLE_USERS_NAME} WHERE {IDENTIFIER_LINE_NAME} = ?
                        '''
        f = self.execute(command, (identifier,), fetch_one=True)

        return f

    def delete_users_table(self):
        command = f'''DROP TABLE {TABLE_USERS_NAME}'''
        self.execute(command, commit=True)
#
# from datetime import datetime
# db = DB()
# # db.delete_users_table()
# # db.create_table_users()
#
# # db.add_user(1123)
# # db.add_user(123)
# # db.update_s_day(1123, datetime.now().timestamp())
# # db.add_user(324)
# print(db.get_users())
# print(db.update_one(1123, -1))
# print(db.get_users())