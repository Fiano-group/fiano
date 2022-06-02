import sqlite3
import os 


class CursorDB():
    def __init__(self):
        self.__dbconnection = None
        self.__dbcursor = None
        self.__path2db = f'{os.getcwd()}/modules/database/fiano.db'
        self.__path2sql = f'{os.getcwd()}/modules/database/fiano.sql'
        try:
            self.__dbconnection = sqlite3.connect(self.__path2db, check_same_thread=False, timeout=5)
            self.__dbcursor = self.__dbconnection.cursor()
        except sqlite3.Error as e:
            print(f'CursorDB: {e}')

    def execute_script(self):
        try:
            script2execute = open(self.__path2sql, 'r').read()
            self.__dbcursor.executescript(script2execute)
        except sqlite3.Error as e:
            print(f'CursorDB: {e}')
        except FileNotFoundError as f:
            print(f'CursorDB: {f}')
        finally:
            self.__dbcursor.close()

    @property
    def cursor(self):
        return self.__dbcursor

    @property
    def connection(self):
        return self.__dbconnection

    def close(self):
        if self.__dbconnection is not None:
            self.__dbconnection.close()