# matura23 some vars and util functions
class Matura23Utils(object):

    labels_map = {
        0 : 'kiwi',
        1 : 'zwetschge',
        2 : 'limette',
        3 : 'zitrone',
        4 : 'passionsfrucht'
    }

    # default
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480

    @staticmethod        
    def getDetectedObjectInfoList(img,results,cameraWidth=CAMERA_WIDTH,cameraHeight=CAMERA_HEIGHT):
        objectInfoList = []

         # in results ist die Liste der erkannten Objekte
        if (len(results) > 0 and results[0] is not None):

            # wir gehen über alle Elemente in der Liste und erstellen ein Objekt mit den Koordinaten und anderen Infos
            for i in range(len(results)):
                eachObjectInfo = {}
                eachObject = results[i]
                # Convert the bounding box figures from relative coordinates
                # to absolute coordinates based on the original resolution
                ymin, xmin, ymax, xmax = eachObject['bounding_box']
                xmin = int(xmin * cameraWidth)
                xmax = int(xmax * cameraWidth)
                ymin = int(ymin * cameraHeight)
                ymax = int(ymax * cameraHeight)
                # object_detection_parameter
                try:
                    eachObjectInfo['x'] = int((xmin+xmax)/2) # center Coordinate default: 320 --> cameraWidth/2
                    eachObjectInfo['y'] = int((ymin+ymax)/2) # center Coordinate default: 240 --> cameraHeight/2
                    eachObjectInfo['width'] = xmax-xmin # width
                    eachObjectInfo['height'] = ymax-ymin # height
                    eachObjectInfo['class_id'] = int(eachObject['class_id'])  # object class_id default: 0
                    eachObjectInfo['label'] = Matura23Utils.labels_map[eachObject['class_id']]  # object label default 'None'
                    eachObjectInfo['count'] = len(results) # number found objects default: 0
                except:
                    print("somethiing went wrong!")

                # Objektinfo der Liste hinzufügen
                objectInfoList.append(eachObjectInfo)       
        else:
            print('no object found')

        return objectInfoList