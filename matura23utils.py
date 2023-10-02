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

                #print("[xmin: {} | xmax: {} | ymin: {} | ymax {}]".format(xmin,xmax,ymin,ymax))

                # Nullpunkt ist oben links im Quadrat
                try:
                    eachObjectInfo['x'] = xmin # x-coordinate
                    eachObjectInfo['y'] = ymin # y-coordinate
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
        foundCount = 0
        notFoundCount = 0
        maxFoundCount = 10
        maxNotFoundCount = 10

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
                
                foundCount = foundCount + 1
                if foundCount >= maxFoundCount:
                    print(foundObjectInfo)
                    return True, foundObjectInfo
                
                time.sleep(0.1)

            else:
                # Wir haben noch nichts gefunden, aber wir versuchen es noch ein paar mal
                # Danach False zurück geben
                # Nichts gefunden, Variable zurückgesetzt
                notFoundCount = notFoundCount + 1
                foundObjectInfo = {}
                foundYcord = 0
                if notFoundCount >= maxNotFoundCount:
                    print('no object found in this position')
                    return False, foundObjectInfo
                
                time.sleep(0.1)


    @staticmethod
    def doGoCloserToFruit(px,foundObjectInfo,cameraWidth,cameraHeight):
        # Zuerst Richtung einschlagen nach Koordinate von Bildern der Kamera
        # Danach mit Echosenosr annähern bis zum gewünschten Abstand
        # True/Fales ob beim Objekt angekommen

        print('doGoCloserToFruit')
        nearFruit = False

        # Einstellungen
        velocity = 10
        drivingTime = 0.5

        # Objekt Werte in Variablen
        xCoord = foundObjectInfo['x']
        yCoord = foundObjectInfo['y']
        width = foundObjectInfo['width']
        height = foundObjectInfo['height']
        classId = foundObjectInfo['class_id']
        label = foundObjectInfo['label']
        count = foundObjectInfo['count'] # number found objects from upper class z.B. 1 out of 3
        centerXCoord = int(xCoord + width/2)
        centerYCoord = int(yCoord + height/2)

        cameraCenterX = int(cameraWidth/2)
        cameraCenterY = int(cameraHeight/2)

        # Zum berechnen der horizontalen Richtung und der Abweichung von der Mitte
        # => links, rechts, Mitte
        deviationX = centerXCoord - cameraCenterX
        directionX = 'forward'
        if deviationX < -10: # -10 als Puffer, deswegen nicht 0
            directionX = 'left'
        elif deviationX > 10:
            directionX = 'right' # fruit right
        else:
            directionX = 'forward'
        

        # Zum berechnen der vertikalen Richtung und der Abweichung von der Mitte
        # => Distanz von der Frucht
        deviationY = centerYCoord - cameraCenterY
        directionY = 'center'
        if deviationY < -10:
            directionY = 'up' # fruit up
        elif deviationY > 10:
            directionY = 'down'
        else:
            directionY = 'center'
        
        #print("{} [directionX: {} | deviationX: {} | directionY: {} | deviationY {}]".format(label,directionX,deviationX,directionY,deviationY))

        # Roboter ausrichten in Richtung der Frucht
        # Max Ausrichtung von Servo 35 pro Richtung
        # eine Hälfte ist cameraWidth/2 (bei 640 Pixel sind es 320 Pixel)
        # Faktor pro Pixel ist 35/320

        steeringFactorPerPixel = int(35/cameraWidth/2)
        angleToObject = int(deviationX*steeringFactorPerPixel)
        if angleToObject < 0:
            angleToObject = max(-35,angleToObject) # -35 kleinster Servowinkel
            for angle in range(0,angleToObject,-1):
                px.set_dir_servo_angle(angle)
                time.sleep(0.01)
        else:
            angleToObject = min(35,angleToObject) # 35 grösster Servowinkel
            for angle in range(0,angleToObject):
                px.set_dir_servo_angle(angle)
                time.sleep(0.01)
                
        print(angleToObject)
        px.forward(velocity)
        time.sleep(drivingTime)
        px.stop()
        time.sleep(5)

        
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