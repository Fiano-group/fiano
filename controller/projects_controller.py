from modules import app
from flask import session, render_template, redirect, url_for, request
import sqlite3 as sql
from modules.database import path2database
import datetime

@app.route("/list_projects")
def list_projects():
    if 'username' in session:
        with sql.connect(path2database) as con:
            context = dict()
            cur = con.cursor()
            cur.execute(f"SELECT * FROM project where id_user = {session['id_user']}")
            projects = cur.fetchall()
            context['projects'] = projects

            return render_template("project.html", **context)
    else:
        return redirect(url_for('login'))



@app.route("/add_project", methods=['POST'])
def newproject():
    if 'username' in session:
        if request.method == 'POST':
            try:
                nameproject = request.form['nameproject']
                dateproject = request.form['dateproject']
                if dateproject is None:
                    dateproject = datetime.datetime.now().strftime('%d/%m/%Y')
                with sql.connect(path2database) as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO project VALUES (?,?,?,?)", (None, nameproject, dateproject, session['id_user']))
                    con.commit()
            except sql.Error as e:
                print(e)
            finally:
                return redirect(url_for("list_projects"))
        return render_template("project.html")
    else:
        return redirect(url_for('login'))


@app.route("/edit_project/<int:id_project>")
def edit_project(id_project):
    if 'username' in session:
        username = session['username']
        with sql.connect(path2database) as con:
            context = dict()
            cur = con.cursor()
            cur.execute(f"SELECT * FROM analysis where id_project = {id_project}")
            analysis = cur.fetchall()
            context['analysis'] = analysis
            session['id_project'] = id_project
            return render_template("analysis.html", **context)
    else:
        return redirect(url_for('login'))


@app.route("/delete_project/<int:id_project>")
def delete_project(id_project):
    if 'username' in session:
        with sql.connect(path2database) as con:
            cur = con.cursor()
            cur.execute(f"delete from project where id_project = {id_project}")
            return redirect(url_for('list_projects'))
    else:
        return redirect(url_for('login'))


@app.route("/return_project")
def return_project():
    if 'username' in session:
        return redirect(url_for('list_projects'))
    return redirect(url_for('login'))