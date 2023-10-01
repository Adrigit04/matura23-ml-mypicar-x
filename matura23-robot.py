#!/usr/bin/env python3
from vilib import Vilib
from picarx import Picarx

import time

from matura23utils import Matura23Utils


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

img = None
results = []

def main():

    Matura23Utils.doStart()

    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True) 
    #Vilib.object_detect_set_model(path='/opt/vilib/detect.tflite')
    #Vilib.object_detect_set_labels(path='/opt/vilib/coco_labels.txt')
    Vilib.object_detect_set_model(path='/opt/vilib/matura23/Run2023-09-30/detect.tflite')
    Vilib.object_detect_set_labels(path='/opt/vilib/matura23/labels.txt')
    Vilib.object_detect_switch(True)

    px = Picarx() # instanzieren, aus Klasse Objekt machen

    countFound = 0
    countNotFound = 0
    countRun = 0


    while True:
        img = Vilib.detect_obj_parameter['object_img']
        results = Vilib.detect_obj_parameter['object_results']
        objectInfoList = Matura23Utils.getDetectedObjectInfoList(img, results, CAMERA_WIDTH, CAMERA_HEIGHT)
        #if len(objectInfoList) > 0:
            #print(objectInfoList)

        # beim ersten mal verändern wir die Position nicht, an Ort und Stelle suchen
        if countRun > 0 
            Matura23Utils.doGoInNewPosition(px,objectInfoList)

        found = Matura23Utils.doSearchFruits(px,objectInfoList)
        if found == True:
            nearFruit = Matura23Utils.doGoCloserToFruit(px,objectInfoList)
            if nearFruit == True:
                Matura23Utils.doPickUpFruit(px,objectInfoList)
                Matura23Utils.doSortInFruit(px,objectInfoList)





        else:
            print('no fruit in this position')
            
        countRun = countRun + 1
    
    Matura23Utils.doEnd()

if __name__ == "__main__":
    main()

