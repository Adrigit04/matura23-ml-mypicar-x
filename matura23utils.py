from vilib import Vilib
import time


# matura23 some vars and util functions
class Matura23Utils(object):

    labels_map = {
        0 : 'kiwi',
        1 : 'zwetschge',
        2 : 'limette',
        3 : 'zitrone',
        4 : 'passionsfrucht'
    }



    sleepSeconds = 0.5

    @staticmethod        
    def getDetectedObjectInfoList(img,results,cameraWidth,cameraHeight):
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
        # else:
            # print('no object found')

        return objectInfoList





    @staticmethod
    def doGoInNewPosition(px,objectInfoList):
        # Neue Suchposition einrichten
        print('doGoInNewPosition')

        for angle in range(0, 35):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)
        px.backward(10)
        time.sleep(0.5)
        px.stop()

        for angle in range(35, -35, -1):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)
        px.forward(10)
        time.sleep(0.5)
        px.stop()

        for angle in range(-35, 0):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)
        

    @staticmethod
    def doSearchFruits(px,objectInfoList,cameraWidth,cameraHeight):
        # Warten um mehrere Bilder abzugleichen
        # => Sicherstellen Frucht und nicht nur falsch angezeigte Frucht
        # gibt True/False zurück je nach dem ob Frucht gefunden
        found = False
        print('doSearchFruits')

        foundObjectInfo = {}
        foundYcord = 0
        while(True):
            img = Vilib.detect_obj_parameter['object_img']
            results = Vilib.detect_obj_parameter['object_results']
            objectInfoList = Matura23Utils.getDetectedObjectInfoList(img, results, cameraWidth, cameraHeight)
            if len(objectInfoList) > 0:
                # Suche das Elemnt, welches zu unterst im Bildschirm ist
                # Gefundenes Objekt in Variable merken, weil es mehrmals geshen werden muss um sicher zu gehen
                # Wenn die Bedingungen erfüllt sind geben wir found = True zurück (return)

                for i in range(len(objectInfoList)):
                    eachObject = objectInfoList[i]
                    if eachObject['y'] > foundYcord:
                        foundYcord = eachObject['y']
                        foundObjectInfo = eachObject
                        print(foundObjectInfo)

                time.sleep(1)


            else:
                # Wir haben noch nichts gefunden, aber wir versuchen es noch ein paar mal
                # Danach False zurück geben
                # Nichts gefunden, Variable zurückgesetzt
                foundObjectInfo = {}
                foundYcord = 0
                time.sleep(1)



        time.sleep(Matura23Utils.sleepSeconds)
        # Code hier der entscheided True/False
        
        found = True

        return found 

    @staticmethod
    def doGoCloserToFruit(px,objectInfoList):
        # Zuerst Richtung einschlagen nach Koordinate von Bildern der Kamera
        # Danach mit Echosenosr annähern bis zum gewünschten Abstand
        # True/Fales ob beim Objekt angekommen
        nearFruit = False
        print('doGoCloserToFruit')
        # Code der entscheided ob Roboter vor der Frucht ist
        time.sleep(Matura23Utils.sleepSeconds)
        
        nearFruit = True

        return nearFruit

    @staticmethod
    def doPickUpFruit(px,objectInfoList):
        # Aufladen der Frucht
        # Vorläufig mit Text to Speech Ausgabe (tts)
        print('doPickUpFruit')
        time.sleep(Matura23Utils.sleepSeconds)

    @staticmethod
    def doSortInFruit(px,objectInfoList):
        # Frucht transportieren zu zugehrigem Slot
        # Vorläufig mit tts
        # Mit einem Counter, damit er nach 5 Früchten fertig wird
        print('doSortInFruit')
        time.sleep(Matura23Utils.sleepSeconds)
        
    @staticmethod
    def doStart():
        # Konfigurationen zum Starten des Codes
        print('doStart')
        
    @staticmethod
    def doEnd():
        # Konfigurationen zum Beenden des Codes
        print('doEnd')