from flask import  render_template, redirect, url_for, request
from modules import app
from modules.login import login 
from modules.database.orm.userDAO import UserDAO
from modules.database.orm.user import User

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if login.valid_login(request.form['username'], request.form['password']):
            return render_template('index.html', username=request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)


@app.route("/add_user", methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['passwd']
        
        userDAO = UserDAO()
        user = User()
        user.name = ''
        user.lastname = ''
        user.email = ''
        user.username = username
        user.password = passwd
        if userDAO.add_user(user):
            return redirect(url_for("home"))
        else:
            return render_template("register.html", error=f'Failed to create user:{user.username}')
        