import sqlite3 as sql 
import bcrypt
from flask import request, render_template, session, redirect, url_for
from modules import app
from modules.login.login import valid_login
from modules.database import path2database


@app.route('/')
def home():
    return redirect(url_for("login"))


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        session.permanent = True
        username = request.form['username']
        if valid_login(username, request.form['password']):
            with sql.connect(path2database) as con:                
                cur = con.cursor()       
                cur.execute(f"select * from user where username = '{username}'")
                user_data = cur.fetchall()
                # context['first_name'] = user_data[0][3]
                # context['last_name'] = user_data[0][4]
                # context['id_user'] = user_data[0][0]
                session['id_user'] = user_data[0][0]
                session['first_name'] = user_data[0][3]
                session['last_name'] = user_data[0][4]
                session['username'] = username
            if 'username' in session:
                return redirect(url_for("list_projects"))
            else:
                return redirect(url_for('login'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():   
    # import os
    # app.config['SECRET_KEY'] = os.urandom(32)
    # session.pop('username', None)
    # return render_template('login.html')
    session.pop('username', None)
    return redirect(url_for('home'))
