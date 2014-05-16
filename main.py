#!/usr/bin/env python
import numpy as np
import cv2
import time
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
ball_state = 0
notFoundCounter=0
isRoaming=False
roamingTimer=0
#variabili per erosione dilatazione
rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(21,21))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(11,11))
#Creazione oggetto della classe
motor = Arduino()
graph = Graph()

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
capture.set(cv2.cv.CV_CAP_PROP_FPS, 15)

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
	minColor = np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
	maxColor = np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
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
			
			
	if (found and not isRoaming and (ball_state >= 2)):
		notFoundCounter = 0
		#cv2.circle(cameraFeed, (c[0],c[1]), c[2], (0,255,0),2)
		cv2.circle(hsvFrame, (x,y), maxRadius, (0,255,0),2)
		print "Le coordinate del centro sono: ("+ str(x) +"," + str(y)+")"
		if enableMotor:
			e = (int)(x)-target #variabile errore >0 oggetto a dx
									#<0 oggetto a sx
			
			#graph.updateVal(e) #update graph
			motor.setMotor(maxRadius,e)
	else:

		if(notFoundCounter<15):
			notFoundCounter+=1
		else:
			isRoaming=True
			roamingTimer+=1
			if(roamingTimer==1):
				motor.setRoaming()
			elif(roamingTimer==15):
				roamingTimer=0
				iRoaming=False
				notFoundCounter=0
				motor.changeSpeed(0,0)

	if enableFrame==0: #visualizzo le immagini 
		#cv2.imshow(mainGui,cameraFeed) #immagine acquisita
		cv2.imshow(hsvWindow, hsvFrame) #immagine con colori HSV
		cv2.imshow(thresholdWindow,thresholded) #immagine Threshold

	#aspetto per un delta_t se l'utente preme ESC per uscire
	escKey = cv2.waitKey(delta_t)
	if escKey==27:
		break
	
	if exit:
		break

saveValue()
cv2.destroyAllWindows()
cv2.VideoCapture(0).release()
#motor.onClose()
