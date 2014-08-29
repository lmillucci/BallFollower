#!/usr/bin/env python
import numpy as np
import cv2
import time
import socket
import thread
#from raspberry import Raspberry
#from beaglebone import BeagleBone
from arduino import Arduino
from graph import Graph

#------ VALORI PREDEFINITI --------
H_MIN = 26
S_MIN = 75
V_MIN = 67
H_MAX = 256
S_MAX = 256
V_MAX = 256

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

#------ FINESTRE -----------
mainGui = "Immagine acquisita"
hsvWindow = "Immagine HSV"
thresholdWindow = "Immagine rilevata"
settingWindow = "Imposta soglia"
blurWindow = "Immagine con filtro Blur"

#------ PARAMETRI UTILI ----------
enableFrame = 0 #Abilita/Disabilita l'update della finestra
enableMotor = 0 #Abilita/Disabilita i motori
target = IMAGE_WIDTH/2 #voglio che l'oggetto stia al centro dello schermo
delta_t = 200 #intervallo di tempo prima di passare al frame successivo
exit = 0 #Permette di uscire dal programma salvando i dati
enableElab = 0 #Abilita/Disabilita l'erosione/dilatazione
kernel = np.ones((5,5),np.uint8) #Kernel per erodi/dilata
ball_state = 0 #permette di ridurre il rumore
roaming_timer = 0 #conta il tempo in cui non vedo palline
spiral = 0 #moltiplicatore per aumentare raggio spirale
manualMode=False #parametro per abilitare modalita maunale
manualDir=None #direzione in modalita manuale
manualSpeed=0 #velocita in modalita manuale

#variabili per erosione dilatazione
rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(21,21))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(11,11))
#Creazione oggetto della classe
motor = Arduino()
#graph = Graph()

#variabili per la gestione del socket
client_socket = None
server_socket = None

def initSocketThread():
        global client_socket
        global server_socket
        TCP_IP = ''
        TCP_PORT = 32239

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server_socket.bind((TCP_IP,TCP_PORT))
        server_socket.listen(5)
        
        while True:
                if (client_socket is None):
                        client_socket, address = server_socket.accept()
                        print "Open socket whit: " , address
                else:
                        thread.exit()

def onTrackbarSlide(*args):
        pass

def saveValue():
        hmin=cv2.getTrackbarPos("H-min",settingWindow)
        smin=cv2.getTrackbarPos("S-min",settingWindow)
        vmin=cv2.getTrackbarPos("V-min",settingWindow)
        hmax=cv2.getTrackbarPos("H-max",settingWindow)
        smax=cv2.getTrackbarPos("S-max",settingWindow)
        vmax=cv2.getTrackbarPos("V-max",settingWindow)
        saveData=str(hmin)+";"+str(smin)+";"+str(vmin)+";"+str(hmax)+";"+str(smax)+";"+str(vmax)
        out_file = open("parametri.txt","w")
        out_file.write(saveData)
        out_file.close()

def loadValue():
        try:
                in_file = open("parametri.txt","r")
                text=in_file.read()
                in_file.close()
                s = text.split(";")
                global H_MIN, S_MIN, V_MIN, H_MAX, S_MAX,V_MAX
                H_MIN = (int)(s[0])
                S_MIN = (int)(s[1])
                V_MIN = (int)(s[2])
                H_MAX = (int)(s[3])
                S_MAX = (int)(s[4])
                V_MAX = (int)(s[5])
                print str(s)
        except Exception as detail:
                print "ERROR: impossible load settings from file", detail

def createSlider():
        cv2.namedWindow(settingWindow,1);
        #metodo che crea le trackbar(label, finestra, valore da cambiare, valore massimo,action listener)
        cv2.createTrackbar("H-min", settingWindow, H_MIN, 256, onTrackbarSlide)
        cv2.createTrackbar("S-min", settingWindow, S_MIN, 256, onTrackbarSlide)
        cv2.createTrackbar("V-min", settingWindow, V_MIN, 256, onTrackbarSlide)
        cv2.createTrackbar("H-max", settingWindow, H_MAX, 256, onTrackbarSlide)
        cv2.createTrackbar("S-max", settingWindow, S_MAX, 256, onTrackbarSlide)
        cv2.createTrackbar("V-max", settingWindow, V_MAX, 256, onTrackbarSlide)
        cv2.createTrackbar("Motori I/O", settingWindow, 0, 1, onTrackbarSlide)
        cv2.createTrackbar("Aggiornamento FRAME", settingWindow, 0, 1, onTrackbarSlide)
        cv2.createTrackbar("Erodi/dilata", settingWindow, 0, 1, onTrackbarSlide)
        cv2.createTrackbar("EXIT", settingWindow, 0, 1, onTrackbarSlide)




#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0);


loadValue()

createSlider()

capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
capture.set(cv2.cv.CV_CAP_PROP_FPS, 20)

try:
        thread.start_new_thread(initSocketThread, ())
except:
        print "ERROR during initSocketThread"

#loop principale del programma
while True:

        #definisco la variabile per i frame catturati
        _,cameraFeed = capture.read()
        cameraFeed = cv2.flip(cameraFeed,1)

        #creo un immagine temporanea per poter applicare il median blur
        tmp = cv2.medianBlur(cameraFeed, 5)


        #variabile su cui salvo l'immagine HSV
        hsvFrame = cv2.cvtColor(tmp,cv2.COLOR_BGR2HSV)

        #filtro hsvFrame cercando solo un determinato range di colori
        #minColor = np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
        #maxColor = np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
        minColor = np.array((H_MIN,S_MIN,V_MIN))
        maxColor = np.array((H_MAX,S_MAX,V_MAX))
        thresholded = cv2.inRange(hsvFrame,minColor, maxColor);

        #Verifico se attivare l elaborazione immagine
        enableElab = cv2.getTrackbarPos("Erodi/dilata",settingWindow)   
        #applico erosione e dilatazione 
        if enableElab == 1:
                thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
                thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)

        #Verifico se attivare il motore
        enableMotor = cv2.getTrackbarPos("Motori I/O",settingWindow)

        #Verifico se attivare i frame
        enableFrame = cv2.getTrackbarPos("Aggiornamento FRAME", settingWindow)

        #Verifico se uscire
        exit = cv2.getTrackbarPos("EXIT",settingWindow)

        #applico Hough
        circles = cv2.HoughCircles(thresholded, cv2.cv.CV_HOUGH_GRADIENT, dp=2, minDist=60, param1=100, param2=40, minRadius=5, maxRadius=60)

        #ATTENZIONE circles e una matrice 1xnx3
        #print circles
        found = False
        if circles is not None:
                maxRadius = 0
                x = 0
                y = 0

                for i in range(circles.size/3):
                        circle=circles[0,i]
                        cv2.circle(hsvFrame, (circle[0],circle[1]), circle[2], (255,0,0),2)
                        if circle[2]>maxRadius:
                                radius=int(circle[2])
                                maxRadius=int(radius)
                                x=int(circle[0])
                                y=int(circle[1])
                found=True
                ball_state += 1
        else:
                ball_state=0

        if(manualMode):
                if(manualDir=="F"):
                        motor.changeSpeed(manualSpeed,manualSpeed)
                elif(manualDir=="L"):
                        motor.changeSpeed(manualSpeed, 20)
                elif(manualDir=="R"):
                        motor.changeSpeed(20, manualSpeed)
                
        elif (found and (ball_state >= 2)):
                roaming_timer = 0 #quando vedo la pallina azzero il contatore dei frame in cui non la trovo
                spiral = 0 #azzero il raggio della spirale quando trovo una pallina
                #cv2.circle(cameraFeed, (c[0],c[1]), c[2], (0,255,0),2)
                cv2.circle(hsvFrame, (x,y), maxRadius, (0,255,0),2)
                print "Le coordinate del centro sono: ("+ str(x) +"," + str(y)+")"
                if enableMotor:
                        e = (int)(x)-target #variabile errore >0 oggetto a dx
                                                                        #<0 oggetto a sx

                        #graph.updateVal(e) #update graph
                        motor.setMotor(maxRadius,e)
        elif (enableMotor and (ball_state==0) and (not manualMode)):
                #se non ho trovato nessuna pallina mi fermo
                roaming_timer += 1 #quando non vedo palline incremento il timer
                #motor.changeSpeed(0,0)
                if roaming_timer % 20 == 0 and roaming_timer<80:
                        #mi fermo
                        motor.changeSpeed(0, 0)
                elif roaming_timer % 15 == 0 and roaming_timer<80:
                        #inizio a girare
                        motor.changeSpeed(22, 35)
                if roaming_timer == 80:
                        #motor.changeSpeed(0, 0)
                        #roaming_timer = 0
                        #left=min(50,30+(7*spiral))
                        #right=min(40,20+(7*spiral))
                        motor.changeSpeed(30,30)
                if roaming_timer > 180:
                        motor.changeSpeed(0, 0)
                        spiral+=1
                        roaming_timer = 0 

        if enableFrame==0: #visualizzo le immagini 
                #cv2.imshow(mainGui,cameraFeed) #immagine acquisita
                cv2.imshow(hsvWindow, hsvFrame) #immagine con colori HSV
                cv2.imshow(thresholdWindow,thresholded) #immagine Threshold

        if not (client_socket is None):
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                #encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                #encoding frame and frame2
                result, imgencoded = cv2.imencode('.jpg', cameraFeed, encode_param)
                result, imgencoded2 = cv2.imencode('.jpg', thresholded, encode_param)
                #creating arrays
                data1 = np.array(imgencoded)
                data2 = np.array(imgencoded2)
                #creating one string
                stringData = data1.tostring() + "separatore" + data2.tostring()
                try:
                        client_socket.send( str(len(stringData)).ljust(16));
                        client_socket.send(stringData);
                except:
                        pass
                try:
                        ricevuto = client_socket.recv(1024)
                        option = ricevuto.split(";")
                        if option[0]=="end":
                            print "Ho ricevuto l'end dal Client"
                            client_socket.close()
                            server_socket.close()
                            client_socket = None
                            server_socket = None
                            try:
                                thread.start_new_thread(initSocketThread, ())
                            except:
                                print "ERROR during initSocketThread"
                            
                        elif option[0]=="comando":
                            if(option[1]=="F"):
                                print "Forward at ",option[2]
                            elif(option[1]=="L"):
                                print "Left at ",option[2]
                            elif(option[1]=="R"):
                                print "Right at ",option[2]
                            manualDir=option[1]
                            manualSpeed=option[2]
                        elif option[0]=="soglie":
                            #global H_MIN, S_MIN, V_MIN, H_MAX, S_MAX,V_MAX
                            H_MIN = int(option[1])
                            S_MIN = int(option[2])
                            V_MIN = int(option[3])
                            H_MAX = int(option[4])
                            S_MAX = int(option[5])
                            V_MAX = int(option[6])
                            print "H_MIN ",H_MIN
                        elif option[0]=="manuale":
                            if option[1]=="on":
                                manualMode=True
                                motor.changeSpeed(0,0)
                                print "manuale"
                            else:
                                manualMode=False
                                motor.changeSpeed(0,0)
                                print "automatico"
                        else:
                            #devo continuare
                            pass
                except:
                        client_socket.close()
                        client_socket = None



        #aspetto per un delta_t se l'utente preme ESC per uscire
        escKey = cv2.waitKey(delta_t)
        if escKey==27:
                break

        if exit:
                break



saveValue()
cv2.destroyAllWindows()
cv2.VideoCapture(0).release()
motor.onClose()
server_socket.close()

