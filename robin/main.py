#!/usr/bin/env python
import numpy as np
import cv2
import time
import socket
import thread
import  cwiid
import time
from arduino import Arduino




#------ FINESTRE -----------
mainGui = "Immagine acquisita"
hsvWindow = "Immagine HSV"
thresholdWindow = "Immagine rilevata"
settingWindow = "Imposta soglia"
blurWindow = "Immagine con filtro Blur"

#------ VALORI PREDEFINITI --------
H_MIN = 26
S_MIN = 75
V_MIN = 67
H_MAX = 256
S_MAX = 256
V_MAX = 256

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

#------ PARAMETRI UTILI ----------
manualMode=True #parametro per abilitare modalita maunale
found=False #parametro che indica se ho trovato la pallina
ball_state= 0 #parametro per contare il numero di framein cui vedo la pallina
roaming_timer = 0 #conta il tempo in cui non vedo palline
spiral = 0 #moltiplicatore per aumentare raggio spirale
target = IMAGE_WIDTH/2 #voglio che l'oggetto stia al centro dello schermo
delta_t = 200 #intervallo di tempo prima di passare al frame successivo
enableMotor = 0 #Abilita/Disabilita i motori
roaming_timer = 0 #conta il tempo in cui non vedo palline
manualDir=None #direzione in modalita manuale
manualSpeed=0 #velocita in modalita manuale
maxRadius=0
wm=None

motor=Arduino()

#variabili per la gestione del socket
client_socket = None
server_socket = None

def initSocketThread():
        global client_socket
        global server_socket
        TCP_IP = ''
        TCP_PORT = 32243

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

#creo i slider
def onTrackbarSlide(*args):
        pass

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

def findCircles(thresholded, hsvFrame):
    global found, ball_state, maxRadius
    #applico Hough
    circles = cv2.HoughCircles(thresholded, cv2.cv.CV_HOUGH_GRADIENT, dp=2, minDist=60, param1=100, param2=40, minRadius=5, maxRadius=60)

    #ATTENZIONE circles e una matrice 1xnx3
    #print circles
    found = False
    x = 0
    if circles is not None:
            maxRadius = 0
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
            cv2.circle(hsvFrame, (x,y), maxRadius, (0,255,0),2)
            print "Le coordinate del centro sono: ("+ str(x) +"," + str(y)+")"
    else:
        ball_state = 0

    return x

def follow(x):
    global roaming_timer, spiral, target, enableMotor, maxRadius
    roaming_timer = 0 #quando vedo la pallina azzero il contatore dei frame in cui non la trovo
    spiral = 0 #azzero il raggio della spirale quando trovo una pallina
    #cv2.circle(cameraFeed, (c[0],c[1]), c[2], (0,255,0),2)
    if enableMotor:
            e = (int)(x)-target #variabile errore >0 oggetto a dx

            motor.setMotor(maxRadius,e)

def roaming():
    global roaming_timer
    #se non ho trovato nessuna pallina mi fermo
    roaming_timer += 1 #quando non vedo palline incremento il timer
    motor.changeSpeed(0,0)

    if roaming_timer % 20 == 0 and roaming_timer<80:
            print "mi fermo"
            motor.changeSpeed(0, 0)
    elif roaming_timer % 15 == 0 and roaming_timer<80:
            print "inizio a girare"
            motor.changeSpeed(22, 35)
    if roaming_timer == 80:
            left=min(50,30+(7*spiral))
            right=min(40,20+(7*spiral))
            motor.changeSpeed(left,right)
    if roaming_timer > 180:
            motor.changeSpeed(0, 0)
            spiral+=1
            roaming_timer = 0

def modeManual2():
    global manualDir, manualSpeed
    if(manualDir=="F"):
            motor.changeSpeed(manualSpeed, manualSpeed)
    elif(manualDir=="L"):
            motor.changeSpeed(manualSpeed, 20)
    elif(manualDir=="R"):
            motor.changeSpeed(20, manualSpeed)
    elif(manualDir=="S"):
            motor.changeSpeed(0, 0)



def modeManual():
    global wm
    if wm is None:
        print("Premi 1+2 per connettere il wiimote")
        time.sleep(2)
        wm=cwiid.Wiimote()
        wm.rpt_mode = cwiid.RPT_BTN
    else:
        button = wm.state['buttons']

        # & serve per fare il confronto bit a bit
        if(button & cwiid.BTN_LEFT):
            print("Ho premuto il tasto sinistro ",button)

        if(button & cwiid.BTN_RIGHT):
            print("Ho premuto il tasto destro",button)

        if(button & cwiid.BTN_UP):
            print("Ho premuto il tasto alto",button)

        if(button & cwiid.BTN_DOWN):
            print("Ho premuto il tasto basso",button)

        if(button & cwiid.BTN_A):
            print("Ho premuto il tasto A",button)

        if(button & cwiid.BTN_B):
            print("Ho premuto il tasto B",button)

        if(button & cwiid.BTN_1):
            print("Ho premuto il tasto 1", button)

        if(button & cwiid.BTN_2):
            print("Ho premuto il tasto 2",button)

        if(button & cwiid.BTN_MINUS):
            print("Ho premuto il tasto -",button)

        if(button & cwiid.BTN_PLUS):
            print("Ho premuto il tasto +",button)

        if(button & cwiid.BTN_HOME):
            print("Ho premuto il tasto HOME",button)
            wm.rumble= True
            time.sleep(1)
            wm.rumble = False

def tXrX(cameraFeed, thresholded):
    global client_socket, server_socket, manualDir, manualSpeed, manualMode, enableMotor
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
            client_socket.send( str(len(stringData)).ljust(16))
            client_socket.send(stringData)
    except:
            pass
    try:
            ricevuto = client_socket.recv(1024)
            print ricevuto
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
                elif(option[1]=="S"):
                    print "Stop"
                manualDir=option[1]
                manualSpeed=option[2]
            elif option[0]=="soglie":
                global H_MIN, S_MIN, V_MIN, H_MAX, S_MAX,V_MAX
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
            elif option[0]=="nomotor":
                if option[1]=="on":
                    enableMotor = 1
                    print "-----------------------------------------------------Enabled motor"
                elif option[1]=="off":
                    enableMotor = 0
                    print "-----------------------------------------------------Disabled motor"
            else:
                #devo continuare
                pass
    except:
            client_socket.close()
            client_socket = None


createSlider()

#variabili per erosione dilatazione
rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(21,21))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(11,11))

#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0)

capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
capture.set(cv2.cv.CV_CAP_PROP_FPS, 20)

loadValue()

#cerco la connessione
try:
        thread.start_new_thread(initSocketThread, ())
except:
        print "ERROR during initSocketThread"

#loop pricipale
while True:

    #Verifico se attivare il motore
    #enableMotor = cv2.getTrackbarPos("Motori I/O",settingWindow)

    #Verifico se attivare i frame
    enableFrame = cv2.getTrackbarPos("Aggiornamento FRAME", settingWindow)

    #Verifico se uscire
    exit = cv2.getTrackbarPos("EXIT",settingWindow)

    #definisco la variabile per i frame catturati
    _,cameraFeed = capture.read()
    cameraFeed = cv2.flip(cameraFeed,1)
    cv2.imshow(thresholdWindow,cameraFeed) #immagine Threshold

    #creo un immagine temporanea per poter applicare il median blur
    tmp = cv2.medianBlur(cameraFeed, 5)

    #variabile su cui salvo l'immagine HSV
    hsvFrame = cv2.cvtColor(tmp,cv2.COLOR_BGR2HSV)

    if manualMode:
        #filtro hsvFrame cercando solo un determinato range di colori
        minColor = np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
        maxColor = np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
        print maxColor
    else:
        minColor = np.array((H_MIN,S_MIN,V_MIN))
        maxColor = np.array((H_MAX,S_MAX,V_MAX))
    thresholded = cv2.inRange(hsvFrame,minColor, maxColor);

    #Verifico se attivare l elaborazione immagine
    #enableElab = cv2.getTrackbarPos("Erodi/dilata",settingWindow)

    #applico erosione e dilatazione
    enableElab = 0
    if enableElab == 1:
            #thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
            #thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
            pass

    #abilitazione modalita automatica
    if manualMode:
        modeManual()
    else:
        x=findCircles(thresholded, hsvFrame)
        if (found and (ball_state >= 2)):
            follow(x)
            print "follow"
        elif (enableMotor and (ball_state==0)):
            print "spirale"

    if not (client_socket is None):
        tXrX(cameraFeed, thresholded)

    cv2.imshow(hsvWindow, hsvFrame) #immagine con colori HSV
    cv2.imshow(thresholdWindow,thresholded) #immagine Threshold
    escKey = cv2.waitKey(delta_t)

    if exit:
        break

saveValue()
cv2.destroyAllWindows()
cv2.VideoCapture(0).release()
motor.onClose()
server_socket.close()
