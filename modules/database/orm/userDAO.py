import sqlite3
from modules.database.dao import DAO
import bcrypt


class UserDAO(DAO):
    def __init__(self):
        DAO.__init__(self)

    def add_user(self, _user):
        hashed_password = bcrypt.hashpw(_user.password.encode('utf-8'), bcrypt.gensalt())
        password = hashed_password.decode('utf-8')
        try:
            self.cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                (None, _user.username, password, _user.name, _user.lastname, _user.email, None)
            )
            self.connection.commit()
            self.connection.close()
            return True
        except sqlite3.Error as e:
            print(f'UserDAO:{e}')
            self.connection.rollback()
            self.connection.close()
            return False
        

        

    