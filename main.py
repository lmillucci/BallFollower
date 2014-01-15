#!/usr/bin/env python
import numpy as np
import cv2
import RPi.GPIO as io

#------ VALORI PREDEFINITI --------
H_MIN = 26
S_MIN = 75
V_MIN = 67
H_MAX = 256
S_MAX = 256
V_MAX = 256

#------ FINESTRE -----------
mainGui="Immagine acquisita"
hsvWindow="Immagine HSV"
thresholdWindow="Immagine rilevata"
settingWindow="Imposta soglia"
blurWindow="Immagine con filtro Blur"

#------ IMPOSTAZIONI ELABORAZIONE ----------
enableElab=False
#------ IMPOSTAZIONI GPIO --------
io.setmode(io.BCM)

io.cleanup() 

in1_pin = 4
in2_pin = 17
pwm_pin= 23
in3_pin = 24
in4_pin = 25
pwm2_pin = 22
 
io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)
io.setup(pwm_pin, io.OUT)
io.setup(in3_pin, io.OUT)
io.setup(in4_pin, io.OUT)
io.setup(pwm2_pin, io.OUT)
p=io.PWM(pwm_pin, 500)
q=io.PWM(pwm2_pin, 500)

def onTrackbarSlide(*args):
    pass





def changeSpeed(value1, value2 ):
	p.ChangeDutyCycle(value1)
	q.ChangeDutyCycle(value2)

 #motore 1
def clockwise():
    io.output(in1_pin, True)    
    io.output(in2_pin, False)
 
def counter_clockwise():
    io.output(in1_pin, False)
    io.output(in2_pin, True)
#motore 2
def orario():
	io.output(in3_pin,True)
	io.output(in4_pin,False)
	
def antiorario():
	io.output(in3_pin,False)
	io.output(in4_pin,True)


def createSlider():
	
	cv2.namedWindow(settingWindow,1);
	
	#metodo che crea le trackbar(label, finestra, valore da cambiare, valore massimo,action listener)
	cv2.createTrackbar("H-min",settingWindow, H_MIN, 256, onTrackbarSlide)
	cv2.createTrackbar("S-min",settingWindow, S_MIN, 256,onTrackbarSlide)
	cv2.createTrackbar("V-min",settingWindow, V_MIN, 256,onTrackbarSlide)
	cv2.createTrackbar("H-max",settingWindow, H_MAX, 256, onTrackbarSlide)
	cv2.createTrackbar("S-max",settingWindow, S_MAX, 256,onTrackbarSlide)
	cv2.createTrackbar("V-max",settingWindow, V_MAX, 256,onTrackbarSlide)
	


# ------- MAIN -------------
#inizializzo i pgin gpio
p.start(0)
p.ChangeDutyCycle(100)
q.start(0)
q.ChangeDutyCycle(100)

cv2.namedWindow(mainGui,1)
#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0);
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 240)
width,height = capture.get(3),capture.get(4)

createSlider()

rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(8,8))

#loop principale del programma
while True:
	#definisco la variabile per i frame catturati
	_,cameraFeed = capture.read()
	cameraFeed = cv2.flip(cameraFeed,1)
	
	#variabile su cui salvo l'immagine HSV
	hsvFrame = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)


	

	#filtro hsvFrame cercando solo un determinato range di colori
	minColor=np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
	maxColor=np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
	thresholded=cv2.inRange(hsvFrame,minColor, maxColor);
	
	#applico erosione e dilatazione 
	if enableElab:
		cv2.erode(thresholded, thresholded,rectErosione)
		cv2.erode(thresholded, thresholded,rectErosione)
		cv2.erode(thresholded, thresholded,rectErosione)
		
		cv2.dilate(thresholded, thresholded, rectDilataz)
		cv2.dilate(thresholded, thresholded, rectDilataz)
		cv2.dilate(thresholded, thresholded, rectDilataz)
	
	#applico Hough
	circles = cv2.HoughCircles(thresholded, cv2.cv.CV_HOUGH_GRADIENT, dp=2, minDist=120, param1=100, param2=40, minRadius=10, maxRadius=60)
	
	#ATTENZIONE circles e una matrice 1xnx3
	#print circles
	
	if circles is not None:
		maxRadius=0
		x=0
		y=0
		found=False
		for i in range(circles.size/3):
			circle=circles[0,i]
			if circle[2]>maxRadius:
				found=True
				radius=int(circle[2])
				maxRadius=int(radius)
				x=int(circle[0])
				y=int(circle[1])
			
			
	if found:
		#cv2.circle(cameraFeed, (c[0],c[1]), c[2], (0,255,0),2)
		cv2.circle(cameraFeed, (x,y), maxRadius, (0,255,0),2)
		
		#se x e minore di 640/3=213-->220 vuol dire che la pallina e troppo a SX
		if x < 220:
			#giro a sx
			clockwise()
			antiorario()
		elif x > 420:
			#giro a dx
			counter_clockwise()
			orario()
		else:
			#vado avanti
			antiorario()
			counter_clockwise()
			
	#visualizzo le immagini 
	cv2.imshow(mainGui,cameraFeed)
	#cv2.imshow(hsvWindow, hsvFrame)
	cv2.imshow(thresholdWindow,thresholded)
	
	if cv2.waitKey(200)==27:
		break
	
