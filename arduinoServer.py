#installing pySerial is required 
import serial 
#TO-DO

ser = ""

class Arduino:
  
    def __init__(self):
      ser = serial.Serial('/dev/tty.usbserial', 9600)
  
  	def changeSpeed(self,value1, value2 ):
  	  pass

    #motore 1
    def motor1Orario(self):
      pass

    def motor1AntiOrario(self):
      pass
    
    #motore 2
    def motor2Orario(self):
      pass
    
    def motor2AntiOrario(self):
      pass
    
    def __init__(self):
      pass
    
    def setMotor(self, u, e):
      pass

    def onClose(self):
      pass
