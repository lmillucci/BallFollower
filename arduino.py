import time
import serial

class Arduino:
	ser = ""
	ENDING = "\n"
	
	def __init__(self):
		self.ser = "Ciao"
		#self.ser = serial.Serial('/dev/ttyACM0', 9600)
		
	def setMotor(self, u, e):
		direction = ""
		if e < -40:
			#turn Left
			print "Left"
			direction = "l" + self.ENDING

		elif e > 40:
			#turn right
			print "Right"
			direction = "r" + self.ENDING

		else:
			#go Forward
			print "Forward"
			u=75
			direction = "f" + self.ENDING
		
		direction += str(u)+ self.ENDING 
		print direction
		#self.ser.write(direction)
	
	def changeSpeed(self, value_left, value_right):
		#TO-DO --> called by 187 in main
		pass
	
	def onClose(self):
		#TO-DO
		pass
