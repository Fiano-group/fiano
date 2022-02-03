from modules import app
from flask import session, request, redirect, flash, render_template, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3 as sql
from modules import ALLOWED_EXTENSIONS
from modules.database import path2database
from pathlib import Path
import shutil

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in  ALLOWED_EXTENSIONS


@app.route("/upload", methods=['POST'])
def uploader():
    if 'username' in session:
        with sql.connect(path2database) as con:         
            cur = con.cursor()
            cur.execute(f"select * from analysis where id_analysis = {session['id_analysis']}")
            data = cur.fetchall()

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            f = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename
            if f.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                analysis_full_path = f"{os.getcwd()}/{data[0][3]}"
                if Path(analysis_full_path).exists():
                    shutil.rmtree(analysis_full_path)
                Path(analysis_full_path).mkdir(parents=True, exist_ok=True)
                f.save(f"{analysis_full_path}/original.jpg")
                return redirect(url_for('edit_analysis', id_analysis=session['id_analysis']))
    else:
        return redirect(url_for('login'))