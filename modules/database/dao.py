from modules.database.cursor import CursorDB

class DAO:
    def __init__(self):
        self.__cursorDB = CursorDB()
        self.__cursor = self.__cursorDB.cursor
        self.__connection = self.__cursorDB.connection

    @property
    def connection(self):
        return self.__connection

    @property
    def cursor(self):
        return self.__cursor

    def close(self):
        if self.__cursorDB:
            self.__cursorDB.close()