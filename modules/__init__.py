from flask import Flask
import os 


app = Flask(__name__, template_folder=os.getcwd()+'/view/templates', static_folder=os.getcwd()+'/view/static')
app.config['UPLOAD_FOLDER'] = './static'
filename = None
path_histogram = None
DATABASE = './users.db'
