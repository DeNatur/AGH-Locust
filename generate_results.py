# This script is to be filled by the team members. 
# Import necessary libraries
# Load libraries
import json
import cv2
from operator import itemgetter
import numpy as np
import imutils
from ctypes import *
import math
import random
import os
import darknet

# Implement a function that takes an image as an input, performs any preprocessing steps and outputs a list of bounding box detections and assosciated confidence score. 


class GenerateFinalDetections():
    
    colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]
    def __init__(self):
        self.seed = 2018
        
        
    def two_points_detect(self, points, tl, tr, bl, br, cc):
         p1, p2 = points
         corners = [{'x': p1[0],'y':p1[1]}, {'x': p2[0],'y':p2[1]}]
         x_sorted_corners = sorted(corners, key=itemgetter('x'))
         y_sorted_corners = sorted(corners, key=itemgetter('y'))
         width = x_sorted_corners[1]['x'] - x_sorted_corners[0]['x']
         height = y_sorted_corners[1]['y'] - y_sorted_corners[0]['y']
         
         if((width > height) and (x_sorted_corners[0]['y'] < cc[1])):
             tl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
             tr = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
             bl = [x_sorted_corners[0]['x'], br[1]]
             br = [x_sorted_corners[1]['x'], br[1]]
             
             bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
             
             bb_all = []
             bb_all.append(bb)
             return bb_all
         elif((width > height) and (x_sorted_corners[0]['y'] > cc[1])):
             bl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
             br = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
             tl = [x_sorted_corners[0]['x'], tr[1]]
             tr = [x_sorted_corners[1]['x'], tr[1]]
            
             bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
            
             bb_all = []
             bb_all.append(bb)
             return bb_all
            
         elif((width < height) and (y_sorted_corners[0]['x'] > cc[0])):
             tr = [y_sorted_corners[0]['x'],y_sorted_corners[0]['y']]
             br = [y_sorted_corners[1]['x'],y_sorted_corners[1]['y']]
             tl = [tl[0],y_sorted_corners[0]['y']]
             bl = [bl[0],y_sorted_corners[1]['y']]
            
             bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
            
             bb_all = []
             bb_all.append(bb)
             return bb_all
            
            
         elif((width < height) and (y_sorted_corners[0]['x'] < cc[0])):
             tl = [y_sorted_corners[0]['x'],y_sorted_corners[0]['y']]
             bl = [y_sorted_corners[1]['x'],y_sorted_corners[1]['y']]
             tr = [tr[0],y_sorted_corners[0]['y']]
             br = [br[0],y_sorted_corners[1]['y']]
             
             bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
            
             bb_all = []
             bb_all.append(bb)
             return bb_all
        
        
    def four_points_detect(self, points):
        p1, p2, p3, p4 = points
        corners = [{'x': p1[0],'y':p1[1]}, {'x': p2[0],'y':p2[1]}, {'x': p3[0],'y':p3[1]}, {'x':p4[0],'y':p4[1]}]
        #print(corners)
        x_sorted_corners = sorted(corners, key=itemgetter('x'))
        #print(x_sorted_corners)
        tl_bl_corners = [x_sorted_corners[0],x_sorted_corners[1]]
        tl_bl_sorted_corners = sorted(tl_bl_corners, key=itemgetter('y'))
        
        tl = [tl_bl_sorted_corners[0]['x'],tl_bl_sorted_corners[0]['y']]
        bl = [tl_bl_sorted_corners[1]['x'],tl_bl_sorted_corners[1]['y']]
        
        tr_br_corners = [x_sorted_corners[2],x_sorted_corners[3]]
        tr_br_sorted_corners = sorted(tr_br_corners, key=itemgetter('y'))
        
        tr = [tr_br_sorted_corners[0]['x'],tr_br_sorted_corners[0]['y']]
        br = [tr_br_sorted_corners[1]['x'],tr_br_sorted_corners[1]['y']]
        bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
        bb_all = []
        bb_all.append(bb)
        return bb_all
    
    
    def three_points_detect(self, points):
        p1, p2, p3 = points
        tl= []
        tr = []
        br = []
        bl = []
        
        
        corners = [{'x': p1[0],'y':p1[1]}, {'x': p2[0],'y':p2[1]}, {'x': p3[0],'y':p3[1]}]
        
        x_sorted_corners = sorted(corners, key=itemgetter('x'))
        y_sorted_corners = sorted(corners, key=itemgetter('y'))    
        
        if((x_sorted_corners[1]['x'] - x_sorted_corners[0]['x']) < (x_sorted_corners[2]['x']) - x_sorted_corners[1]['x']):
        
            ccx = int((x_sorted_corners[0]['x'] + x_sorted_corners[1]['x'])/2)
            ccy = int((x_sorted_corners[0]['y'] + x_sorted_corners[1]['y'])/2)
            
            if(ccy >= x_sorted_corners[2]['y']):
                tr = [x_sorted_corners[2]['x'], x_sorted_corners[2]['y']]
                if(x_sorted_corners[0]['y'] < x_sorted_corners[1]['y']):
                    tl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
                    bl = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    br = [tr[0], bl[1]]
                else:
                    tl = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    bl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
                    br = [tr[0], bl[1]]
            else:
                br = [x_sorted_corners[2]['x'], x_sorted_corners[2]['y']]
                if(x_sorted_corners[0]['y'] < x_sorted_corners[1]['y']):
                    tl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
                    bl = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    tr = [br[0], tl[1]]
                else:
                    tl = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    bl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
                    tr = [br[0], tl[1]]
                    
        else:
            
            ccx = int((x_sorted_corners[1]['x'] + x_sorted_corners[2]['x'])/2)
            ccy = int((x_sorted_corners[1]['y'] + x_sorted_corners[2]['y'])/2)
            
            if(ccy >= x_sorted_corners[0]['y']):
                tl = [x_sorted_corners[0]['x'], x_sorted_corners[0]['y']]
                if(x_sorted_corners[1]['y'] < x_sorted_corners[2]['y']):
                    tr = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    br = [x_sorted_corners[2]['x'],x_sorted_corners[2]['y']]
                    bl = [tl[0],br[1]]
                else:
                    tr = [x_sorted_corners[2]['x'],x_sorted_corners[2]['y']]
                    br = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    bl = [tl[0], br[1]]
            else:
                bl = [x_sorted_corners[0]['x'],x_sorted_corners[0]['y']]
                if(x_sorted_corners[1]['y'] < x_sorted_corners[2]['y']):
                    tr = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    br = [x_sorted_corners[2]['x'],x_sorted_corners[2]['y']]
                    tl = [bl[0],tr[1]]
                else:
                    tr = [x_sorted_corners[2]['x'],x_sorted_corners[2]['y']]
                    br = [x_sorted_corners[1]['x'],x_sorted_corners[1]['y']]
                    tl = [bl[0],tr[1]]
        
        bb = [tl[0],tl[1],tr[0],tr[1],br[0],br[1],bl[0],bl[1]]
        
        bb_all = []
        bb_all.append(bb)
        return bb_all
        
        
    def predict(self,img):
        bb_all = []
        #Punkt od którego wychodzi wektor
        pt1 = (int(img.shape[1] /2), int(img.shape[0] /2))
        results = []
        temp_results = darknet.performDetect(showImage=False, weightPath = "bin/yolo-obj_10000.weights")
        for result in temp_results:
            xl = int(result[2][0]) - int(result[2][2]/2)
            yl = int(result[2][1]) - int(result[2][3]/2)
            xr = int(result[2][0]) + int(result[2][2]/2)
            yr = int(result[2][1]) + int(result[2][3]/2)
            topleft = {'x': xl, 'y': yl}
            bottomright = {'x': xr, 'y': yr}
            results.append({'label': 'gate', 'confidence': result[1], 'topleft': topleft, 'bottomright': bottomright})
        sorted_results = sorted(results, key=lambda k: k['confidence'], reverse=True) 
        
        nr = 1
        points = []
        #print(sorted_results)
        
        for color, result in zip(self.colors, sorted_results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            
            
            x = int((tl[0] + br[0])/2)
            y = int((tl[1] + br[1])/2)
            
            p1 = [x,y]
            points.append(p1)
        
            label = result['label']
            img = cv2.rectangle(img, tl, br, color, 5)
                       
            nr += 1
            if nr == 5:
                break
        #print(points)
        if(len(points) == 4):
            bb_all = self.four_points_detect(points)
        elif(len(points) == 3):
            bb_all = self.three_points_detect(points)
            
        else:
            
            results2 = []
            temp_results2 = darknet.performDetect(showImage=False, weightPath = "bin/yolo-obj.weights")
            for result in temp_results2:
                xl = int(result[2][0]) - int(result[2][2]/2)
                yl = int(result[2][1]) - int(result[2][3]/2)
                xr = int(result[2][0]) + int(result[2][2]/2)
                yr = int(result[2][1]) + int(result[2][3]/2)
                topleft = {'x': xl, 'y': yl}
                bottomright = {'x': xr, 'y': yr}
                results2.append({'label': 'gate', 'confidence': result[1], 'topleft': topleft, 'bottomright': bottomright})
            tl= []
            tr = []
            br = []
            bl = []
            
            sorted_results2 = sorted(results2, key=lambda k: k['confidence'], reverse=True)
            for color, result in zip(self.colors, sorted_results2):
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                
                tr = [br[0],tl[1]]
                bl = [tl[0],br[1]]
                
                ccx = int((tl[0] + br[0])/2)
                ccy = int((tl[1] + br[1])/2)
                img = cv2.rectangle(img, tl, br, color, 5)     
                cc = [ccx, ccy]
                if(len(points) ==2):
                    bb_all = self.two_points_detect(points, tl, tr, bl, br, cc)
                   
                        
        #print(bb_all)
        if bb_all == None:
            bb_all = []
        if type(bb_all) is not list:
            bb_all.tolist()
        if len(bb_all) == 0:
            bb = []
            bb_all.append(bb)
        else:
            pt2 = (int((bb_all[0][0] + bb_all[0][4]) / 2), int((bb_all[0][1] + bb_all[0][5]) / 2))
            
        
        #print(bb_all)
        dir1 = ""
        dir2 = ""
        odl1 = 1
        odl2 = 0
        width_up = 0
        width_down = 0
        height_left = 0
        height_right = 0
        if len(bb_all[0]) is not 0:
            bb_test = []
            x1,y1,x2,y2,x3,y3,x4,y4 = bb_all[0]
            bb_test.extend([[x1,y1]])
            bb_test.extend([[x2,y2]])
            bb_test.extend([[x3,y3]])
            bb_test.extend([[x4,y4]])
            bb_test = np.asarray(bb_test)
            width_up = x2 - x1
            width_down = x3 - x4
            
            height_left = y4 - y1
            height_right = y3 - y2
            cv2.drawContours(img, [bb_test], -1, (0, 255, 0), 10)
            pt2 = (int((bb_all[0][0] + bb_all[0][4]) / 2), int((bb_all[0][1] + bb_all[0][5]) / 2))
            cv2.arrowedLine(img, pt1, pt2, (0,0,255), 5)
            if pt2[0] - pt1[0] > 0:
                dir1 = "RIGHT"
            else:
                dir1 = "LEFT"
            
            odl1 = pt2[1] - pt1[1]
            odl2 = pt2[0] - pt1[0]
            if pt2[1] - pt1[1] > 0:
                dir2 = "DOWN"
            else:
                dir2 = "UP"
            #img = cv2.putText(img, dir1 + " " + dir2, (50,400), cv2.FONT_HERSHEY_SIMPLEX ,  
             #      1, (255, 0, 0), 2, cv2.LINE_AA)
        
        
        #cv2.imshow('img', img)
        return img, dir2, dir1, odl1, odl2, width_up, width_down, height_left, height_right
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
                
    

    
    
    
        

   