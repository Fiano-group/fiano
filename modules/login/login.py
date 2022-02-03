import bcrypt
import sqlite3 as sql
from modules.database import path2database

def valid_login(username, password):
    with sql.connect(path2database, check_same_thread=False) as con:
        cur = con.cursor()
        sql_sentence = 'select password from User where username = ?'
        result = cur.execute(sql_sentence, (username,)).fetchall()
        if len(result) != 0 and result is not None:
            db_password = result[0][0].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), db_password)
    return False
    