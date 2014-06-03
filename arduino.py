import time
import serial

class Arduino:
	ENDING = "\n"
	
	def __init__(self):
		self.u = 0
		self.ser = serial.Serial('/dev/ttyACM0', 9600)
		
	def setMotor(self, radius, e):
		direction = ""
		if(2 * radius > 100):
			self.u = 60
			print "Forward"
			direction = "8" + self.ENDING
		else:
			min_range = abs(5.3 * radius)			
			if( e < min_range and e > -min_range):
				self.u = 60
				print "Forward"
				direction = "8" + self.ENDING
			else:
				self.u = (int)((10 / (320 - min_range)) * (abs(e) - min_range) + 20) 
				if e > 0: 
					print "Right"
					direction = "6" + self.ENDING
				if e < 0:
					print "Left"
					direction = "4" + self.ENDING
		
		direction += str(self.u) + self.ENDING + "0" + self.ENDING
		print direction
		self.ser.write(direction)

	def setRoaming(self):
		direction="5"+self.ENDING+"0"+self.ENDING + "0" + self.ENDING
		self.ser.write(direction)

	
	def changeSpeed(self, value_left, value_right):
		direction="5" + self.ENDING + str(value_left) + self.ENDING + str(value_right) + self.ENDING
		print direction
		self.ser.write(direction)
	
	def onClose(self):
		#mi fermo mettendo a 0 entrambi i motori
		self.changeSpeed(0,0)
