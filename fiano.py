
import sys
sys.path.append('modules/')
sys.path.append('controller/')
import sqlite3

import controller
from modules import app
from modules.database.cursor import CursorDB

def __start_database():
    db = None
    try:
        db = CursorDB()
        sql_sentence = "SELECT count(*) FROM sqlite_master WHERE type='table'"
        tables_number = db.cursor.execute(sql_sentence).fetchall()
        if tables_number[0][0] == 0:            
            try:
                db.execute_script()
            except sqlite3.Error as e:
                print(f'__start_database:{e}')
        else:
            print(f'__start_database: Using previous configuration of database')
    except sqlite3.Error as error:
        print(f'__start_database:{e}')
    finally:
        db.close()

if __name__ == "__main__":
    __start_database()
    app.run(host='0.0.0.0', port='1234', debug=True, use_reloader=False)