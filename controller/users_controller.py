from modules import app
from flask import render_template, request
import bcrypt
import sqlite3 as sql
from modules.database import path2database

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/add_user", methods=['POST'])
def add_user():
    if request.method == 'POST':
        try:
            username = request.form['username']
            passwd = request.form['passwd']
            passwd_confirmation = request.form['passwd_confirmation']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            if passwd != passwd_confirmation:
                msg = "La contraseña no coincide"
                return render_template("register.html", msg = msg)
            else:
                hashed_password = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())
                password = hashed_password.decode('utf-8')

                print(username, passwd)
            with sql.connect(path2database) as con:
                cur = con.cursor()
                cur.execute("INSERT INTO User VALUES (?, ?, ?, ?, ?, ?)", (None, username, password, first_name, last_name, email))
                con.commit()
                msg = "Record successfully added"
        except sql.Error as e:
            con.rollback()
            print(e)
            msg = "error in insert operation"
        finally:
            return render_template("login.html", msg = msg)
            con.close()
    return render_template('register.html')
