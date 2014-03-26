#!/usr/bin/env python
import numpy as np
import cv2
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
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

#------ IMPOSTAZIONI Finestra ----------
enableFrame=0
#------ IMPOSTAZIONI MOTORI ----------
enableMotor=0

#------ IMPOSTAZIONI GPIO --------
#io.setmode(io.BCM)

GPIO.cleanup()

#------ setting 4 GPIO ----------------  TO CHANGE
in1_pin = "P9_11"
in2_pin = "P9_12"
in3_pin = "P9_13"
in4_pin = "P9_14"
#------ setting 2 PWM -----------------  TO CHANGE
pwm1_pin= "P8_13"
pwm2_pin = "P8_19"
 
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)

#PWM.start(pin,duty,frequency,polarity)
PWM.start(pwm1_pin, 0, 500, 1)
PWM.start(pwm2_pin,0,500,1)



def onTrackbarSlide(*args):
    pass



def changeSpeed(value1, value2 ):
	PWM.set_duty_cycle(pwm1_pin,value1)
	PWM.set_duty_cycle(pwm1_pin,value1)

#motore 1
def motor1Orario():
	GPIO.output(in1_pin, GPIO.HIGH)    
	GPIO.output(in2_pin, GPIO.LOW)
 
def motor1AntiOrario():
	GPIO.output(in1_pin, GPIO.LOW)
	GPIO.output(in2_pin, GPIO.HIGH)
#motore 2
def motor2Orario():
	GPIO.output(in3_pin,GPIO.HIGH)
	GPIO.output(in4_pin,GPIO.LOW)
	
def motor2AntiOrario():
	GPIO.output(in3_pin,GPIO.LOW)
	GPIO.output(in4_pin,GPIO.HIGH)





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
	cv2.createTrackbar("Aggiornamento FRAME",settingWindow,0,1,onTrackbarSlide)
	
	


# ------- MAIN -------------

#------- VARIABILI APPOGGIO PID -----
E=0
old_e=0

target=IMAGE_WIDTH/2 #voglio che l'oggetto stia al centro dello schermo
delta_t=125 #intervallo di tempo prima di passare al frame successivo

cv2.namedWindow(mainGui,1)
#imposto la sorgente per l'acquisizione
# 0 -> cam predefinita
# 1 -> cam esterna
capture = cv2.VideoCapture(0);

width,height = capture.get(3),capture.get(4)

createSlider()

capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)

#loop principale del programma
while True:
	#time.sleep(1) #dopo un movimento aspetto un secondo per fissare l'immagine
	#definisco la variabile per i frame catturati


	_,cameraFeed = capture.read()
	cameraFeed = cv2.flip(cameraFeed,1)

		

	#variabile su cui salvo l'immagine HSV
	hsvFrame = cv2.cvtColor(cameraFeed,cv2.COLOR_BGR2HSV)

	#filtro hsvFrame cercando solo un determinato range di colori
	minColor=np.array((cv2.getTrackbarPos("H-min",settingWindow),cv2.getTrackbarPos("S-min",settingWindow),cv2.getTrackbarPos("V-min",settingWindow)))
	maxColor=np.array((cv2.getTrackbarPos("H-max",settingWindow),cv2.getTrackbarPos("S-max",settingWindow),cv2.getTrackbarPos("V-max",settingWindow)))
	thresholded=cv2.inRange(hsvFrame,minColor, maxColor);
	
	#Verifico se attivare il motore
	enableMotor=cv2.getTrackbarPos("Motori I/O",settingWindow)
	
	#Verifico se attivare i frame
	enableFrame=cv2.getTrackbarPos("Aggiornamento FRAME", settingWindow)

	
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
			
			e = (int)(x)-target #variabile errore >0 oggetto a dx
									#<0 oggetto a sx
			Kp=0.75 #Metto .0 affinche vengano trattati come decimali
			Ki=0.0
			Kd=0.0
			E=(E+e)*(delta_t/1000)
			e_dot=(e-old_e)/(delta_t/1000)
			old_e=e
			Up = Kp * e
			Ui = Ki * E
			Ud = Kd * e_dot
			
			u = int(abs(Up + Ud + Ui))

			changeSpeed(u,u)
			print "Valocita = "+str(u)+ " errore = "+str(e)+ " abs = "+str(abs(e)/(target*1.0))
			
			#decido la direzione da prendere. Uso +-10 e non 0 per avere un minimo di tolleranza
			if e < -40:
				#giro a dx
				print "giro sx"
				motor1AntiOrario()
				motor2AntiOrario()

			elif e > 40:
				#giro a dx
				print "giro dx"
				motor1Orario()
				motor2Orario()


			else:
				#vado avanti
				print "vado avanti"
				changeSpeed(80,80)
				motor2Orario()
				motor1AntiOrario()
				#motor1AntiOrario()
				#motor2AntiOrario()
			
	
	if enableFrame==0:
		#visualizzo le immagini 
		cv2.imshow(mainGui,cameraFeed) #immagine acquisita
		#cv2.imshow(hsvWindow, hsvFrame) #immagine con colori HSV
		cv2.imshow(thresholdWindow,thresholded) #immagine Threshold

	
	#aspetto per un delta_t se l'utente preme ESC per uscire
	if cv2.waitKey(delta_t)==27:
		break
		
	#alla fine del circlo fermo i motori
	changeSpeed(0,0)
	
	if enableMotor:
		#Se attivo enableMotor abbasso il numero di FPS	acquisiti
		delta_t=375
		time.sleep(0.500) # aspetto un secondo per far stabilizzare l'immagine 
	else:
		delta_t=200
		
PWM.stop(pwm1_pin)
PWM.stop(pwm2_pin)
PWM.cleanup()
GPIO.cleanup()
cv2.destroyAllWindows()
cv2.VideoCapture(0).release()
	
