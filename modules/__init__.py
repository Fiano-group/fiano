import os 
from flask import Flask
from datetime import timedelta
from flask_login import LoginManager


app = Flask(__name__, template_folder=os.getcwd()+'/views/templates', static_folder=os.getcwd()+'/views/static')
app.config['UPLOAD_FOLDER'] = 'views/static/files'

app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SECRET_KEY'] = 'erAvJS2cEpOPZsm-9UTEI7bfA'
app_login_manager = LoginManager()
app_login_manager.session_protection = 'strong'
ALLOWED_EXTENSIONS = {'jpg','png'}
filename = None
path_histogram = None

