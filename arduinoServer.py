#installing pySerial is required 
import serial 
import time

ser = ""
ENDING = "\n"


class Arduino:
    def changeSpeed(self,value1, value2 ):
    	pass
    	
    def motor1Orario(self):
    	pass
	def motor1AntiOrario(self):
		pass
	def motor2Orario(self):
		pass
	def motor2AntiOrario(self):
		pass
	def onClose(self):
		pass
	def setMotor(self,u,e):
		direction = ""
		if e < -40:
			#giro a dx
			print "giro sx"
			direction ="l"

		elif e > 40:
			#giro a dx
			print "giro dx"
			direction = "r"


		else:
			#vado avanti
			print "vado avanti"
			u=75
			direction = "f"
		
		direction += ENDING+ str(u)+ENDING+ str(u)+ENDING
		print direction
		ser.write(direction)
    
    def __init__(self):
		global ser
		ser = serial.Serial('/dev/ttyACM0', 9600)
		self.onClose()

a = Arduino()
#a.setMotor(50,50)
