# import os
# import cv2
# import shutil
# import numpy as np
# import thinning
# import bcrypt
# from flask import Flask, request, render_template, Response, url_for, redirect, session
# from datetime import timedelta
# from flask_login import LoginManager
# from werkzeug.utils import secure_filename
# # from matplotlib import pyplot as plt
# from matplotlib.figure import Figure

# import sqlite3 as sql
# from flask import g

import sys
sys.path.append('modules/')
sys.path.append('controller/')
sys.path.append('views/')
import controller
from modules import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='1234', debug=True)