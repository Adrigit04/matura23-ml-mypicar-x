from vilib import Vilib
from robot_hat import TTS

import time
import os



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
    def doGoInNewPosition(px,objectInfoList):
        # Neue Suchposition einrichten
        print('doGoInNewPosition')

        for angle in range(0, 35):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)
        px.backward(10)
        time.sleep(0.5)
        px.stop()
        time.sleep(0.5)

        for angle in range(35, -35, -1):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)
        px.forward(10)
        time.sleep(0.5)
        px.stop()
        time.sleep(0.5)

        for angle in range(-35, 0):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)

        time.sleep(0.5)
        

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
        maxFoundCount = 3
        maxNotFoundCount = 20
        lastFoundObjectInfo = {}

        while(True):

            time.sleep(0.1)
            img = Vilib.detect_obj_parameter['object_img']
            results = Vilib.detect_obj_parameter['object_results']
            objectInfoList = Matura23Utils.getDetectedObjectInfoList(img, results, cameraWidth, cameraHeight)
            if len(objectInfoList) > 0:
                # Suche das Elemnt, welches zu unterst im Bildschirm ist
                # Anzahl Durchläufe in Variable merken,
                # weil es mehrmals geshen werden muss um sicher zu gehen das keine falscher Treffer
                # Wenn die Bedingungen erfüllt sind geben wir found = True zurück (return)

                for i in range(len(objectInfoList)):
                    eachObject = objectInfoList[i]
                    if eachObject['y'] > foundYcord:
                        foundYcord = eachObject['y']
                        foundObjectInfo = eachObject

                    # Damit er wenn er gefundene Früchte aus dem Auge verliert nicht gleich aufgibt 
                    # und in eine neue Position geht, merkt er sich die gefunden Frucht
                    # und versucht zuerst diese Frucht trotzdem zu finden
                    lastFoundObjectInfo = foundObjectInfo


                
                foundCount = foundCount + 1
                if foundCount >= maxFoundCount: # erst wenn es mehrmals gefunden wurde
                    print("[doSearchFruit] object found:{}".format(foundObjectInfo))
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

                    # Wenn bereits eine Frucht gesehen, versucht er diese nun trotzdem zu fidnen
                    # Wenn er diese aber nicht findet, geht er trotzdem weiter
                    # um zu verhidnern, dass er jeder falsch geshenen Frucht nachgeht
                    if lastFoundObjectInfo != {}:
                        foundObjectInfo = lastFoundObjectInfo
                        lastFoundObjectInfo = {}
                    else:
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

        # workaround: Weil Servo nicht auf 0 einstellbar von der rechten Seite (+35)
        Matura23Utils.workaroundSetAngleZero(px)
        time.sleep(0.1)


        # Annähern mit Hilfe von minecart_plus.py
        try:
            lastAngleToObject = 0
            lastDirectionX = 'stop'
            fruitLabel = foundObjectInfo['label']
            found = True
            while found == True and nearFruit == False:
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
                directionX = Matura23Utils.getDirectionX(deviationX)

                # Zum berechnen der vertikalen Richtung und der Abweichung von der Mitte
                # => Distanz von der Frucht
                deviationY = centerYCoord - cameraCenterY
                directionY = Matura23Utils.getDirectionY(deviationY)
                
                print("{} [directionX: {} | deviationX: {} | directionY: {} | deviationY {}]".format(label,directionX,deviationX,directionY,deviationY))

                # Roboter ausrichten in Richtung der Frucht
                # Max Ausrichtung von Servo 35 pro Richtung
                # eine Hälfte ist cameraWidth/2 (bei 640 Pixel sind es 320 Pixel)
                # Faktor pro Pixel ist 35/320
                steeringFactorPerPixel = (35/(cameraWidth/2))
                angleToObject = int(deviationX*steeringFactorPerPixel)
                print("Start angleToObject1:{}".format(angleToObject))
                print(angleToObject,lastAngleToObject)
                print(directionX,lastDirectionX)

                #------------------------------------------------------------------------
                # Servo lässt sich nicht beliebig klein bewegen, deswegen Fixwert gesetzt
                #------------------------------------------------------------------------
                if angleToObject > 15:
                    angleToObject = 20
                elif angleToObject < -15:
                    angleToObject = -20
                else:
                    directionX = 'forward'

                if directionX != "stop":
                    lastDirectionX = directionX

                if directionX == 'forward':
                    # Echosensor ansteuern um Stückweise an Objekt zu gelangen
                    targetDistance = 20
                    distance = round(px.ultrasonic.read(), 2)
                    if distance <= targetDistance:
                        nearFruit = True
                        print('in front of object')
                        break

                    # wenn forwärts gerade aus
                    Matura23Utils.workaroundSetAngleZero(px)
                    px.forward(velocity)
                    time.sleep(0.5)
                    px.stop()

                    # Echosensor ansteuern um Stückweise an Objekt zu gelangen
                    targetDistance = 20
                    distance = round(px.ultrasonic.read(), 2)
                    if distance <= targetDistance:
                        nearFruit = True
                        print('in front of object')
                        break


                elif directionX == 'right':
                    # lenken nach links ein, weil wir Rückwärts fahren
                    # danach ein bisschen vorwärts
                    for angle in range(0,-angleToObject,-1):
                        px.set_dir_servo_angle(angle)
                        time.sleep(0.01)
                    px.backward(velocity)
                    time.sleep(0.4)
                    px.stop()
                    Matura23Utils.workaroundSetAngleZero(px)
                    time.sleep(1)
                    px.forward(velocity)
                    time.sleep(0.4)
                    px.stop()
                    time.sleep(0.5)

                elif directionX == 'left':
                    # lenken nach rechts ein, weil wir Rückwärts fahren
                    # danach ein bisschen vorwärts
                    for angle in range(0,-angleToObject):
                        px.set_dir_servo_angle(angle)
                        time.sleep(0.01)
                    px.backward(velocity)
                    time.sleep(0.4)
                    px.stop()
                    Matura23Utils.workaroundSetAngleZero(px)
                    time.sleep(1)
                    px.forward(velocity)
                    time.sleep(0.4)
                    px.stop()
                    time.sleep(0.5)

                else:
                    print("unknown direction to {}".format(label))
                    Matura23Utils.workaroundSetAngleZero(px)

                time.sleep(0.1)
                px.stop()
                print("END angelToObject:{}".format(angleToObject))


                # neues Bild wird ausgelesen
                found,foundObjectInfo = Matura23Utils.getFoundObjectInfo(cameraWidth,cameraHeight,fruitLabel)

        except Exception as e:
            # Handle any type of error and print a custom error message
            print("Error:", e)
                   
        finally:
            px.stop()
            print("stop and exit")
            time.sleep(0.1)

        if nearFruit == True:
            print('in front of object')


        return nearFruit
    

    @staticmethod
    def doPickUpFruit(px,foundObjectInfo):
        label = foundObjectInfo['label']
        # Aufladen der Frucht
        # Vorläufig mit Text to Speech Ausgabe (tts)
        print('doPickUpFruit')

        words = ["found {}".format(label)]
        tts_robot = TTS()
        for i in words:
            print(i)
            tts_robot.say(i)

        # Mit Echosensor warten, bis Objekt entfernt wird
        fruitInFront = True
        targetDistance = 30
        fruitNotInFront = 0
        while fruitInFront == True:
            distance = round(px.ultrasonic.read(), 2)
            time.sleep(0.1)
            if distance > targetDistance:
                fruitNotInFront = fruitNotInFront + 1

            if fruitNotInFront > 5:
                fruitInFront = False

        time.sleep(1)

        words = ["thank you for picking up {}".format(label)]
        tts_robot = TTS()
        for i in words:
            print(i)
            tts_robot.say(i)


    @staticmethod
    def doSortInFruit(px,foundObjectInfo):
        label = foundObjectInfo['label']
        # Frucht transportieren zu zugehrigem Slot
        # Vorläufig mit tts
        # Mit einem Counter, damit er nach 5 Früchten fertig wird
        print('doSortInFruit')
        time.sleep(0.5)

        words = ["bring {} to correct slot".format(label)]
        tts_robot = TTS()
        for i in words:
            print(i)
            tts_robot.say(i)
        
        


        
    @staticmethod
    def doStart():
        # Konfigurationen zum Starten des Codes
        print('doStart')
        # workaround because tts isn't working without this code
        # https://forum.sunfounder.com/t/picar-x-speaker-not-working/289/2
        os.system('sudo killall pulseaudio')
        
        
    @staticmethod
    def doEnd():
        # Konfigurationen zum Beenden des Codes
        print('doEnd')






#########################################################################################
# Hilfsfunktionen
#########################################################################################

    @staticmethod        
    def getDetectedObjectInfoList(img,results,cameraWidth,cameraHeight):
        objectInfoList = []
        excludedFruitList = ['zitrone']

            # in results ist die Liste der erkannten Objekte
        if (len(results) > 0 and results[0] is not None):

            # wir gehen über alle Elemente in der Liste und erstellen ein Objekt mit den Koordinaten und anderen Infos
            for i in range(len(results)):
                eachObjectInfo = {}
                eachObject = results[i]
                # Zitrone ausklammern
                currentLabel = Matura23Utils.labels_map[eachObject['class_id']]
                if currentLabel not in excludedFruitList:
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
    def workaroundSetAngleZero(px):
        for angle in range(0,-35,-1):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)

        for angle in range(-35,0):
            px.set_dir_servo_angle(angle)
            time.sleep(0.01)



    @staticmethod
    def getDirectionX(deviationX):
        if deviationX < -10: # -10 als Puffer, deswegen nicht 0
            directionX = 'left'
        elif deviationX > 10:
            directionX = 'right' # fruit right
        else:
            directionX = 'forward'
        return directionX

    @staticmethod
    def getDirectionY(deviationY):
        if deviationY < -10:
            directionY = 'up' # fruit up
        elif deviationY > 10:
            directionY = 'down'
        else:
            directionY = 'center'
        return directionY

    @staticmethod
    def getFoundObjectInfo(cameraWidth,cameraHeight,fruitLabel=""):
        # Wie bei Search Methode, Erkennung stabilisieren
        # nicht gleich Code abbrechen wenn einmal Frucht nicht gefunden
        # und nicht gleich zum Objekt fahren wenn nur einmal Frucht gesehen (evtl.falsch gesehene Frucht)
        foundYCoord = 0
        foundObjectInfo = {}
        found = False
        foundCount = 0
        notFoundCount = 0
        maxFoundCount = 3
        maxNotFoundCount = 10

        while foundCount < maxFoundCount and notFoundCount < maxNotFoundCount:
            # Das Bild der gefundenen Frucht wird eingelesen
            img = Vilib.detect_obj_parameter['object_img']
            results = Vilib.detect_obj_parameter['object_results']
            objectInfoList = Matura23Utils.getDetectedObjectInfoList(img, results, cameraWidth, cameraHeight)
            
            # Suchen ob die Frucht mit bestimmtem Label
            if len(objectInfoList) > 0:
                # Suche das Elemnt, welches zu unterst im Bildschirm ist und gleich fruitLabel ist
                for i in range(len(objectInfoList)):
                    eachObject = objectInfoList[i]
                    if eachObject['y'] > foundYCoord and eachObject['label'] == fruitLabel:
                        foundYCoord = eachObject['y']
                        foundObjectInfo = eachObject
                        found = True
            
            else:
                found = False
                foundObjectInfo = {}

            if found == True:
                foundCount = foundCount + 1
            else:
                notFoundCount = notFoundCount + 1

        print(foundObjectInfo)
        return found,foundObjectInfo