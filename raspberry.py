import RPi.GPIO as io

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

class Raspberry:

	def changeSpeed(self,value1, value2 ):
		p.ChangeDutyCycle(value1)
		q.ChangeDutyCycle(value2)

	#motore 1
	def motor1Orario(self):
		io.output(in1_pin, True)    
		io.output(in2_pin, False)
	 
	def motor1AntiOrario(self):
		io.output(in1_pin, False)
		io.output(in2_pin, True)
	#motore 2
	def motor2Orario(self):
		io.output(in3_pin,True)
		io.output(in4_pin,False)
		
	def motor2AntiOrario(self):
		io.output(in3_pin,False)
		io.output(in4_pin,True)

	#inizializzo i pin gpio
	p.start(0)
	p.ChangeDutyCycle(0)
	q.start(0)
	q.ChangeDutyCycle(0)


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
		p.stop()
		q.stop()
		io.cleanup()

