import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM

GPIO.cleanup()

#------ setting 4 GPIO ----------------  TO CHANGE
in1_pin = "P9_11"
in2_pin = "P9_12"
in3_pin = "P9_13"
in4_pin = "P9_14"
#------ setting 2 PWM -----------------  TO CHANGE
pwm1_pin= "P8_13"
pwm2_pin = "P9_21"
 
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)

#PWM.start(pin,duty,frequency,polarity)
PWM.start(pwm1_pin, 0, 500, 0)
PWM.start(pwm2_pin,0,500,0)

class BeagleBone:

	def changeSpeed(self,value1, value2 ):
		PWM.set_duty_cycle(pwm1_pin,value1)
		PWM.set_duty_cycle(pwm2_pin,value2)

	#motore 1
	def motor1Orario(self):
		GPIO.output(in1_pin, GPIO.HIGH)    
		GPIO.output(in2_pin, GPIO.LOW)
	 
	def motor1AntiOrario(self):
		GPIO.output(in1_pin, GPIO.LOW)
		GPIO.output(in2_pin, GPIO.HIGH)
	#motore 2
	def motor2Orario(self):
		GPIO.output(in3_pin,GPIO.HIGH)
		GPIO.output(in4_pin,GPIO.LOW)
		
	def motor2AntiOrario(self):
		GPIO.output(in3_pin,GPIO.LOW)
		GPIO.output(in4_pin,GPIO.HIGH)
		
	def setMotor(self,u,e):
		self.changeSpeed(u,u)
		print "Velocita = "+str(u)+ " errore = "+str(e)
		
		#decido la direzione da prendere. Uso +-10 e non 0 per avere un minimo di tolleranza
		if e < -40:
			#giro a dx
			print "giro sx"
			self.motor1AntiOrario()
			self.motor2AntiOrario()

		elif e > 40:
			#giro a dx
			print "giro dx"
			self.motor1Orario()
			self.motor2Orario()


		else:
			#vado avanti
			print "vado avanti"
			self.changeSpeed(80,80)
			self.motor2Orario()
			self.motor1AntiOrario()
			#motor1AntiOrario()
			#motor2AntiOrario()
			
	def onClose(self):
		PWM.stop(pwm1_pin)
		PWM.stop(pwm2_pin)
		PWM.cleanup()
		GPIO.cleanup()	
