from threading import local
from time import sleep
from controller.analysis_controller import edit_analysis
from  modules import app
from flask import session, request, render_template, redirect, url_for
import cv2
import sqlite3 as sql
import numpy as np
import thinning

from modules.fiano.processing import fiber_analysis

@app.route("/process", methods=['POST'])
def processimage():
    if 'username' in session:
        id_analysis = session['id_analysis']
        if request.method == 'POST':
            local_path  = f'views/static/files/{id_analysis}'
            fiber_analysis(local_path)
            sleep(5)
            return redirect(url_for('edit_analysis', id_analysis = id_analysis))
    else:
        return redirect(url_for('login'))

