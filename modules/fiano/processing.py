import numpy as np 
import cv2
import thinning
from pathlib import Path 
import os
from matplotlib.figure import Figure
from matplotlib import pyplot as plt


def removeIntersection(skeleton, image, region):
    output = image.copy()
    for i in np.arange(0, skeleton.shape[0]-1):
        for j in np.arange(0, skeleton.shape[1]-1):
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

def paths2map(_local_path):
    paths_map = {
        'erosion' : f'{_local_path}/erosion.jpg',    
        'dilation' : f'{_local_path}/dilation.jpg',
        'threshold' : f'{_local_path}/threshold.jpg',
        'skeleton' : f'{_local_path}/skeleton.jpg',
        'histogram' : f'{_local_path}/histogram.jpg',
        'processed':  f'{_local_path}/processed.jpg'
    }
    return paths_map

def fiber_analysis(_local_path):
    paths_map = paths2map(_local_path)
    for path in paths_map.values():
        if Path(path).exists():
            os.remove(path)
    image = cv2.imread(f'{_local_path}/original.jpg')    
    # print(filename)
    # image = cv2.resize(image, (512,512))
    clone = image.copy()
    clone = cv2.cvtColor(clone, cv2.COLOR_RGB2GRAY)
    retval, clone = cv2.threshold(clone, 200, 255, cv2.THRESH_OTSU)
    cv2.imwrite(paths_map['threshold'], clone)
    clone = cv2.bitwise_not(clone)
    clone = cv2.erode(clone, np.ones((3,3), np.ubyte))
    cv2.imwrite(paths_map['erosion'], clone)
    clone = cv2.dilate(clone, np.ones((3,3), np.ubyte))
    cv2.imwrite(paths_map['dilation'], clone)
    #skeleton = thinning(clone)
    skeleton = thinning.guo_hall_thinning(clone.copy())
    cv2.imwrite(paths_map['skeleton'], skeleton)
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
    region = 60
    skel_nointersect = removeIntersection(skeleton, skeleton, region)
    clone_nointersect = removeIntersection(skeleton, clone, region)
    #connected components
    retval, cc, statistics, centroids = cv2.connectedComponentsWithStats(skel_nointersect)
    #statistics
    mean_per_element = np.zeros(retval)
    total_per_element = np.zeros(retval)
    seed_per_element = [0]*retval
    counts_per_measure = np.zeros(60)
    # Parameters histogram x,y
    fiber_range = 60
    x = np.arange(0,fiber_range)
    y = np.zeros(fiber_range)
    eq_a = 0.35539095323861947
    eq_b = 0.816814709295901
    for i in np.arange(0, cc.shape[0]):
        for j in np.arange(0, cc.shape[1]):
            mean_per_element[cc[i,j]] += distTransform[i,j]
            total_per_element[cc[i,j]] += 1
            if seed_per_element[cc[i,j]] == 0:
                seed_per_element[cc[i,j]] = (j,i)
            estimated_measure  = distTransform[i,j]*3*eq_a + eq_b
            if cc[i,j] != 0:
                counts_per_measure[np.uint(np.round(estimated_measure))]+= 1
            # Histogram
            if skel_nointersect[i,j] == 255:
                y[int(estimated_measure)] += 1

    mean_per_element = mean_per_element/total_per_element

    # plt.bar(x,y)
    # plt.xticks(x)
    fig = Figure()
    fig.set_size_inches(20.5,12.5)
    ax = fig.subplots()
    ax.set_xticks(x)
    ax.bar(x,y)
    # ax.plot([x,y])
    fig.savefig(paths_map['histogram'])
   
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
        # This is the equation that we fitted with our data
        estimated_measure  = mean_per_element[c]*3*eq_a + eq_b
        if estimated_measure > 19 and estimated_measure <=23:
            COLOR = BABY
        elif estimated_measure > 23 and estimated_measure <= 26.5:
            COLOR = SF
        elif estimated_measure > 26.5 and estimated_measure <= 29:
            COLOR = H2
        elif estimated_measure > 29 and estimated_measure <= 31.5:
            COLOR = AG
        elif estimated_measure > 31.5:
            COLOR = GR
        cv2.floodFill(final, None, seed_per_element[c], COLOR)
        cv2.putText(
            final,
            str(round(estimated_measure,1)),
            (int(centroids[c][0])+10, int(centroids[c][1])+10),
            cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255),2)

    cv2.imwrite(paths_map['processed'], final)