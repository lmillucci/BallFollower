from matplotlib import pyplot as plt
import numpy as np

class Graph:
	def __init__(self):
		plt.ion()
		ax1=plt.axes() 
 
		self.ydata = [0] * 50
		# make plot
		self.line, = plt.plot(self.ydata)
		plt.ylim([10,40])

	def updateVal(self,value):
		
		ymin = float(min(self.ydata))-10
		ymax = float(max(self.ydata))+10
		plt.ylim([ymin,ymax])
		self.ydata.append(value)
		del self.ydata[0]
		self.line.set_xdata(np.arange(len(self.ydata)))
		self.line.set_ydata(self.ydata)  # update the data
		plt.draw() # update the plot


