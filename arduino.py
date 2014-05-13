import time
import serial

class Arduino:
	ENDING = "\n"
	
	def __init__(self):
		self.ser = "Ciao"
		self.ser = serial.Serial('/dev/ttyACM0', 9600)
		
	def setMotor(self, u, e):
		direction = ""
		if e < -80:
			#turn Left
			print "Left"
			direction = "4" + self.ENDING

		elif e > 80:
			#turn right
			print "Right"
			direction = "6" + self.ENDING

		else:
			#go Forward
			print "Forward"
			#u=75
			direction = "8" + self.ENDING
		
		direction += str(u) + "\n"
		print direction
		self.ser.write(direction)
	
	def changeSpeed(self, value_left, value_right):
		direction="8" + self.ENDING + "0" + "\n"
		print direction
		self.ser.write(direction)
	
	def onClose(self):
		#TO-DO
		pass
