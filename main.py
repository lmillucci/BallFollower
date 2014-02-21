#!/usr/bin/env python
import numpy as np
import cv2
import RPi.GPIO as io
import time

#------ VALORI PREDEFINITI --------
H_MIN = 26
S_MIN = 75
V_MIN = 67
H_MAX = 256
S_MAX = 256
V_MAX = 256

IMAGE_WIDTH=160
IMAGE_HEIGHT=120

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
	cv2.createTrackbar("Motori I/O",settingWindow,0,1,onTrackbarSlide)
	


# ------- MAIN -------------
#inizializzo i pin gpio
p.start(0)
p.ChangeDutyCycle(0)
q.start(0)
q.ChangeDutyCycle(0)


enableMotor=0 #variabile per abilitare i motori

target=IMAGE_WIDTH/2 #voglio che l'oggetto stia al centro dello schermo
delta_t=250 #intervallo di tempo prima di passare al frame successivo

cv2.namedWindow(mainGui,1)
#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0);

width,height = capture.get(3),capture.get(4)

createSlider()

rectErosione = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
rectDilataz = cv2.getStructuringElement( cv2.MORPH_RECT,(8,8))



#loop principale del programma
while True:
	time.sleep(1)
	#definisco la variabile per i frame catturati
	capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)

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
	
	#Verifico se attivare il motore
	enableMotor=cv2.getTrackbarPos("Motori I/O",settingWindow)
	
	#applico Hough
	circles = cv2.HoughCircles(thresholded, cv2.cv.CV_HOUGH_GRADIENT, dp=2, minDist=120, param1=100, param2=40, minRadius=10, maxRadius=60)
	
	#ATTENZIONE circles e una matrice 1xnx3
	#print circles
	found=False
	if circles is not None:
		maxRadius=0
		x=0
		y=0
		
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
		print "Le coordinate del centro sono: ("+ str(x) +"," + str(y)+")"
		if enableMotor:
			
			e = x-target #variabile errore >0 oggetto a dx
										#<0 oggetto a sx
			Kp=100
			u = int(Kp * (abs(e)/(target *1.0)))

			changeSpeed(u,u)
			print "Valocita = "+str(u)+ " errore = "+str(e)+ " abs = "+str(abs(e)/(target*1.0))
			
			#decido la direzione da prendere. Uso +-10 e non 0 per avere un minimo di tolleranza
			if e < -10:
				#giro a dx
				print "giro sx"
				clockwise()
				antiorario()
			elif e > 10:
				#giro a dx
				print "giro dx"
				counter_clockwise()
				orario()
			else:
				#vado avanti
				print "vado avanti"
				changeSpeed(80,80)
				#antiorario()
				#counter_clockwise()
			
	#visualizzo le immagini 
	cv2.imshow(mainGui,cameraFeed) #immagine acquisita
	#cv2.imshow(hsvWindow, hsvFrame) #immagine con colori HSV
	cv2.imshow(thresholdWindow,thresholded) #immagine Threshold
	
	#aspetto per un delta_t se l'utente preme ESC per uscire
	if cv2.waitKey(delta_t)==27:
		break
		
	if enableMotor:
		#Se attivo enableMotor abbasso il numero di FPS	acquisiti
		delta_t=375
		
	#alla fine del circlo fermo i motori
	changeSpeed(0,0)
	
p.stop()
q.stop()
io.cleanup()
	
