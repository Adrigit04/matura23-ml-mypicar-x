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
    maxHits = 5
    foundObjectInfo = {}

    time.sleep(5)
    while countFound < maxHits:
        img = Vilib.detect_obj_parameter['object_img']
        results = Vilib.detect_obj_parameter['object_results']
        objectInfoList = Matura23Utils.getDetectedObjectInfoList(img, results, CAMERA_WIDTH, CAMERA_HEIGHT)
        #if len(objectInfoList) > 0:
            #print(objectInfoList)

        found = False
        nearFruit = False
        try:
            foundObjectInfo = {'label': 'kiwi'}

            Matura23Utils.doStart()

            if (False):
                Matura23Utils.doGoInNewPosition(px,objectInfoList)
                time.sleep(3)

            if (True):
                found,foundObjectInfo = Matura23Utils.doSearchFruits(px,objectInfoList,CAMERA_WIDTH,CAMERA_HEIGHT)
                time.sleep(0.1)

            #if (found == True):
                #nearFruit = Matura23Utils.doGoCloserToFruit(px,foundObjectInfo, CAMERA_WIDTH, CAMERA_HEIGHT)
                #break

            if (False):
                Matura23Utils.doPickUpFruit(px,foundObjectInfo)
            
            if (False):
                Matura23Utils.doSortInFruit(px,foundObjectInfo)
            
            Matura23Utils.doEnd()

            print("found:{} | nearFruit:{}".format(found, nearFruit))
        #except:
            #print("error occurred!!!!")
        except Exception as e:
            # Handle any type of error and print a custom error message
            print("Error:", e)

        finally:
            print("finished")

if __name__ == "__main__":
    main()

