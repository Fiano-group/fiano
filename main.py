import os
import cv2
import shutil
import numpy as np
import thinning
import bcrypt
from flask import Flask, request, render_template, Response, url_for, redirect
# from matplotlib import pyplot as plt
from matplotlib.figure import Figure

import sqlite3 as sql
from flask import g

import sys
sys.path.append('controller')
sys.path.append('modules')


########## Inicio login en la base de datos ##########


def log_the_user_in(username):
    return render_template('index.html', username=username)


########## Fin login en la base de datos ##########
########## Inicio carga de imágenes ##########

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
            hashed_password = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt())
            password = hashed_password.decode('utf-8')

            print(username, passwd)
            with sql.connect("users.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO User VALUES (?, ?)", (username, password))
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
        
        return render_template('index.html', **context)
        

########## Fin de procesamiento de imágenes ##########

############ Inicio de histograma ###########
# @app.route("/histogram", methods=['POST'])
# def histogram():
#     print("segundo histogram "+path_histogram)
#     return render_template('index.html', path_histogram=path_histogram)
############ Fin de histograma ##############

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='1234', debug=False)