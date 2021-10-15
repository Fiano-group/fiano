import os
import cv2
import shutil
import numpy as np
import thinning
import bcrypt
from flask import Flask, request, render_template, Response, url_for, redirect, session
from datetime import timedelta
from flask_login import LoginManager
from werkzeug.utils import secure_filename
# from matplotlib import pyplot as plt
from matplotlib.figure import Figure

import sqlite3 as sql
from flask import g

app = Flask(__name__, template_folder=os.getcwd()+'/templates', static_folder=os.getcwd()+'/static')
app.config['UPLOAD_FOLDER'] = './static'

app.permanent_session_lifetime = timedelta(minutes=5)

app.config['SECRET_KEY'] = 'erAvJS2cEpOPZsm-9UTEI7bfA'
app_login_manager = LoginManager()
app_login_manager.session_protection = 'strong'
ALLOWED_EXTENSIONS = {'jpg','png'}
filename = None
path_histogram = None

DATABASE = './users.db'

########## Inicio login en la base de datos ##########

def valid_login(username, password):
    with sql.connect("users.db", check_same_thread=False) as con:
        cur = con.cursor()
        sql_sentence = 'select password from User where username = ?'
        result = cur.execute(sql_sentence, (username,)).fetchall()
        if len(result) != 0 and result is not None:
            db_password = result[0][0].encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), db_password)
    return False
    

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        session.permanent = True
        username = request.form['username']
        if valid_login(username, request.form['password']):
            session['username'] = username
            if 'username' in session:
                return redirect(url_for("list_projects"))
            else:
                return redirect(url_for('login'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

################ Fin login en la base de datos #################
##################### begin logout users #######################
@app.route('/logout')
def logout():
    # import os
    # app.config['SECRET_KEY'] = os.urandom(32)
    # session.pop('username', None)
    # return render_template('login.html')
    session.pop('username', None)
    return redirect(url_for('home'))
##################### end logout users #########################

######### Inicio obtener todos los proyectos #############

@app.route("/list_projects")
def list_projects():
    if 'username' in session:
        username = session['username']
        with sql.connect("users.db") as con:
            context = dict()
            cur = con.cursor()       
            cur.execute(f"select * from User where username = '{session['username']}'")
            user_data = cur.fetchall()
            context['first_name'] = user_data[0][3]
            context['last_name'] = user_data[0][4]
            context['id_user'] = user_data[0][0]
            session['IDUSER'] = user_data[0][0]
            cur.execute(f"SELECT * FROM Project where idUser = {user_data[0][0]}")
            data = cur.fetchall()
            context['data'] = data
        
            return render_template("project.html", **context)
    else:
        return redirect(url_for('login'))

######## Fin obtener todos los proyectos ###########

######## Crear un nuevo proyecto ##############

@app.route("/add_project", methods=['POST'])
def newproject():
    if 'username' in session:
        if request.method == 'POST':
            try:
                nameproject = request.form['nameproject']
                dateproject = request.form['dateproject']
                with sql.connect("users.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO Project VALUES (?,?,?,?)", (None, nameproject, dateproject, session['IDUSER']))
                    con.commit()
            except sql.Error as e:
                print(e)
            finally:
                return redirect(url_for("list_projects"))
        return render_template("project.html")
    else:
        return redirect(url_for('login'))

################## Fin crear un proyecto ###################
################## Inicio Editar un proyecto ###############

@app.route("/editproject/<int:id_project><string:name_project>")
def editproject(id_project, name_project):
    if 'username' in session:
         with sql.connect("users.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Analysis")
            data = cur.fetchall()
            return render_template("analysis.html", id_project=id_project, name_project=name_project, data=data)
    else:
        return redirect(url_for('login'))

################# Fin Editar un proyecto ###################
################# Inicio obtener todos los analisis #################

@app.route("/analysis")
def listanalysis():
    if 'username' in session:
        with sql.connect("users.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Analysis")
            data = cur.fetchall()
            return render_template("analysis.html", data = data)
    else:
        return redirect(url_for('login'))
################# Fin obtener todos los analisis ####################
################# Inicio crear un nuevo analysis ####################

@app.route("/add_analysis", methods=['POST'])
def newanalysis():
    if 'username' in session:
        if request.method == 'POST':
            try:
                nameanalysis = request.form['nameanalysis']
                dateanalysis = request.form['dateanalysis']
                with sql.connect("users.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO Analysis VALUES (?,?,?,?)", (None, nameanalysis, dateanalysis, 9))
                    con.commit()
            except sql.Error as e:
                con.rollback()
                print(e)
            finally:
                    return redirect(url_for("listanalysis"))
        return render_template("analysis.html")
    else:
        return redirect(url_for('login'))
   

################# Fin crear un nuevo analysis #######################
################# Inicio editar un analysis #########################

@app.route("/editanalysis/<int:id_analysis><string:name_analysis>")
def editanalysis(id_analysis, name_analysis):
    if 'username' in session:
        return render_template("results.html", id_analysis=id_analysis, name_analysis=name_analysis)
    else:
        return redirect(url_for('login'))

################# Fin editar un analysis ############################
################ Inicio carga de imágenes ##################

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in  ALLOWED_EXTENSIONS

@app.route("/upload", methods=['POST'])
def uploader():
    if 'username' in session:
        global filename
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
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                local_filename = 'static/' + filename
                return render_template('results.html', filename=local_filename)
    else:
        return redirect(url_for('login'))
########## Fin carga de imágenes ##########

########## Inicio registro de usuarios ##########

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
            with sql.connect("users.db") as con:
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

########## Fin registro de usuarios ##########

########## Inicio de procesamiento de imágenes ##########

def removeIntersection(skeleton, image, region):
    output = image.copy()
    for i in np.arange(0, skeleton.shape[1]-1):
        for j in np.arange(0, skeleton.shape[0]-1):
            if skeleton[i,j] == 255:
                counter = 0
                if skeleton[i-1,j] == 255: counter+=1
                if skeleton[i-1,j-1] == 255: counter+=1
                if skeleton[i,j-1] == 255: counter+=1
                if skeleton[i+1,j-1] == 255: counter+=1
                if skeleton[i+1,j] == 255: counter+=1
                if skeleton[i+1,j+1] == 255: counter+=1
                if skeleton[i,j+1] == 255: counter+=1
                if skeleton[i-1,j+1] == 255: counter+=1
                if counter > 2:
                    output[i-region:i+region, j-region:j+region] = 0
    return output


@app.route("/process", methods=['POST'])
def processimage():
    global path_histogram
    if request.method == 'POST':
        path_erosion = f'static/process/erosion_{filename}'
        path_dilatation = f'static/process/dilatation_{filename}'
        path_thresholding = f'static/process/thresholding_{filename}'
        path_skeleton = f'static/process/skeleton_{filename}'
        # Histogram
        path_histogram = f'static/process/histogram_{filename}'

        image = cv2.imread('static/' + filename)
        # print(filename)
        image = cv2.resize(image, (512,512))
        clone = image.copy()
        clone = cv2.cvtColor(clone, cv2.COLOR_RGB2GRAY)
        retval, clone = cv2.threshold(clone, 200, 255, cv2.THRESH_OTSU)
        cv2.imwrite(path_thresholding, clone)
        clone = cv2.bitwise_not(clone)
        clone = cv2.erode(clone, np.ones((3,3), np.ubyte))
        cv2.imwrite(path_erosion, clone)
        clone = cv2.dilate(clone, np.ones((3,3), np.ubyte))
        cv2.imwrite(path_dilatation, clone)
         #skeleton = thinning(clone)
        skeleton = thinning.guo_hall_thinning(clone.copy())
        cv2.imwrite(path_skeleton, skeleton)
        #eliminating spurs borders
        skeleton[:,0] = 0 # left
        skeleton[len(skeleton)-1,:] = 0 # bottom
        skeleton[:,skeleton.shape[0]-1] = 0 #right
        skeleton[0,:] = 0 #upper
        #distance transform
        distTransform = cv2.distanceTransform(clone, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        dtn = np.array(distTransform.shape, dtype=np.ubyte)
        distTransformNorm = cv2.normalize(distTransform, dtn, 0, 1, cv2.NORM_MINMAX)
        #deleting intersections
        region = 15
        skel_nointersect = removeIntersection(skeleton, skeleton, region)
        clone_nointersect = removeIntersection(skeleton, clone, region)
        #connected components
        retval, cc, statistics, centroids = cv2.connectedComponentsWithStats(skel_nointersect)
        #statistics
        mean_per_element = np.zeros(retval)
        total_per_element = np.zeros(retval)
        seed_per_element = [0]*retval
        counts_per_measure = np.zeros(50)
        pixel2micron = 3.0

        # Parameters histogram x,y
        fiber_range = 45
        x = np.arange(0,fiber_range)
        y = np.zeros(fiber_range)
       
        for i in np.arange(0, cc.shape[1]):
            for j in np.arange(0, cc.shape[0]):
                mean_per_element[cc[i,j]] += distTransform[i,j]
                total_per_element[cc[i,j]] += 1
                if seed_per_element[cc[i,j]] == 0:
                    seed_per_element[cc[i,j]] = (j,i)
                if cc[i,j] != 0:
                    counts_per_measure[np.uint(np.round(distTransform[i,j]*pixel2micron))]+=1    

                # Histogram
                if skel_nointersect[i,j] == 255:
                    y[int(distTransform[i,j]*pixel2micron)] += 1
                
        mean_per_element = mean_per_element/total_per_element
       
        # plt.bar(x,y)
        # plt.xticks(x)
        fig = Figure()
        fig.set_size_inches(20.5,12.5)
        ax = fig.subplots()
        ax.set_xticks(x)
        ax.bar(x,y)
        # ax.plot([x,y])
        fig.savefig(path_histogram)
        print("primer histogram"+path_histogram)
        #CLASSIFICATION
        final = cv2.cvtColor(clone_nointersect, cv2.COLOR_GRAY2BGR)
        #Color classification
        RY = (255,255,153) # ROYAL
        BABY = (255,255,153) # BABY ALPACA
        SF = (51,255,153) # SUPER FINA o FLEECE
        H2 = (0,255,255) # ALPACA MEDIUM
        AG = (204,204,255) # HUARIZO
        GR = (204,0,204) # GRUESA
        for c in np.arange(1,retval):
            COLOR = RY
            if mean_per_element[c]*pixel2micron > 19 and mean_per_element[c]*pixel2micron <=23:
                COLOR = BABY
            elif mean_per_element[c]*pixel2micron > 23 and mean_per_element[c]*pixel2micron <= 26.5:
                COLOR = SF
            elif mean_per_element[c]*pixel2micron > 26.5 and mean_per_element[c]*pixel2micron <= 29:
                COLOR = H2
            elif mean_per_element[c]*pixel2micron > 29 and mean_per_element[c]*pixel2micron <= 31.5:
                COLOR = AG
            elif mean_per_element[c]*pixel2micron > 31.5:
                COLOR = GR
            cv2.floodFill(final, None, seed_per_element[c], COLOR)
            cv2.putText(final,str(round(mean_per_element[c]*pixel2micron,4)), (seed_per_element[c][0]+10,seed_per_element[c][1]+10),cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,255,255))

        outfilename = f'static/process/final_{filename}' 
        print(outfilename)
        cv2.imwrite(outfilename, final)
        context = dict()
        context['filename'] = 'static/' + filename
        context['outfilename'] = outfilename
        context['path_erosion'] = path_erosion
        context['path_dilatation'] = path_dilatation
        context['path_thresholding'] = path_thresholding
        context['path_skeleton'] = path_skeleton
        context['path_histogram'] = path_histogram
        
        return render_template('results.html', **context)
        

########## Fin de procesamiento de imágenes ##########

############ Inicio de histograma ###########
# @app.route("/histogram", methods=['POST'])
# def histogram():
#     print("segundo histogram "+path_histogram)
#     return render_template('index.html', path_histogram=path_histogram)
############ Fin de histograma ##############

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='1234', debug=True)