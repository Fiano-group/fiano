import bcrypt
import sqlite3
import os 


def valid_login(username, password):
    path2database = os.getcwd()+'/modules/database/users.db'
    with sqlite3.connect(path2database, check_same_thread=False) as con:
        cur = con.cursor()
        sql_sentence = 'select password from User where username = ?'
        result = cur.execute(sql_sentence, (username,)).fetchall()
        if len(result) == 0:
            return False
        db_password = result[0][0].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), db_password)
    return False