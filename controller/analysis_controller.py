from datetime import date
from typing import ValuesView
from modules import app
from flask import session, render_template, url_for, redirect, request
import sqlite3 as sql
from modules.database import path2database
from modules.fiano.processing import paths2map
import datetime
from pathlib import Path
import os


@app.route("/list_analysis")
def list_analysis():
    if 'username' in session:
        with sql.connect(path2database) as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM analysis where id_project = {session['id_project']}")
            analysis = cur.fetchall()
            return render_template("analysis.html", analysis = analysis)
    else:
        return redirect(url_for('login'))


@app.route("/return_analysis")
def return_analysis():
     if 'username' in session:
         return redirect(url_for('list_analysis'))
     return redirect(url_for('login'))



@app.route("/add_analysis", methods=['POST'])
def add_analysis():
    if 'username' in session:
        if request.method == 'POST':
            try:
                nameanalysis = request.form['nameanalysis']
                dateanalysis = request.form['dateanalysis']
                if dateanalysis is None:
                    dateanalysis = datetime.datetime.now().strftime('%d/%m/%Y')
                with sql.connect(path2database) as con:
                    cur = con.cursor()
                    cur.execute(f"select seq from sqlite_sequence where name = 'analysis'")
                    id = cur.fetchall()[0][0]
                    folder_path = f"{app.config['UPLOAD_FOLDER']}/{id+1}"
                    values = (None, nameanalysis, dateanalysis, f'{folder_path}', session['id_user'], session['id_project'])
                    cur.execute("INSERT INTO analysis VALUES (?,?,?,?,?,?)", values)
                    con.commit()
            except sql.Error as e:
                con.rollback()
                print(e)
            finally:
                return redirect(url_for("list_analysis"))                            
    else:
        return redirect(url_for('login'))


@app.route("/edit_analysis/<int:id_analysis>")
def edit_analysis(id_analysis):
    if 'username' in session:
        with sql.connect(path2database) as con:
            context = dict()
            cur = con.cursor()           
            cur.execute(f"select * from analysis where id_analysis = {id_analysis}")
            session['id_analysis'] = id_analysis
            data = cur.fetchall()
            context['data'] = data 
            original = f"/static/files/{id_analysis}/original.jpg"
            if not Path(f"{data[0][3]}/original.jpg").exists():
                original = None
            context['original'] = original
            paths = paths2map(f"static/files/{id_analysis}")
            print(paths)
            for path in paths.keys():
                if Path(f"views/{paths[path]}").exists():
                    context[path] = f"/{paths[path]}"
            print(context)
            return render_template("results.html", **context)
    else:
        return redirect(url_for('login'))


@app.route("/delete_analysis/<int:id_analysis>")
def delete_analysis(id_analysis):
    if 'username' in session:       
        with sql.connect(path2database) as con:
            context = dict()
            cur = con.cursor()
            cur.execute(f"delete from analysis where id_analysis = {id_analysis}")
            return redirect(url_for('list_analysis'))
    else:
        return redirect(url_for('login'))

