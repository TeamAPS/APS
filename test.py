import sys
import serial
from PyQt5 import QtWidgets, uic
import serial.tools.list_ports
import time

# Create a list of the used serial ports

availableSerialPorts = serial.tools.list_ports.comports()

##############################################################

# Read and use the .ui file
qtCreatorFile = "test.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class APSGUI(QtWidgets.QMainWindow, Ui_MainWindow):
	
	# Class intialization
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.APSsetupStatus.setText("Please set up the APS")
		self.findPlaneLimits.setEnabled(False)
		self.comPort = None
		
		# Populate the COM port list
		self.comPortChoice.addItem("None Selected")
		for serialPort in availableSerialPorts:
			self.comPortChoice.addItem(str(serialPort))
		self.comPortChoice.currentIndexChanged.connect(self.connectArduino)
		self.findPlaneLimits.clicked.connect(self.getLimits)
	
	
	def connectArduino(self):
		# The first space is where the port name ends
		comPort = self.comPortChoice.currentText().partition(" ")[0]
		if comPort.startswith("COM"):
			self.comPort = comPort
			self.findPlaneLimits.setEnabled(True)
		else:
			self.findPlaneLimits.setEnabled(False)
	
	def getLimits(self):
		# Baud rate is 9600	
		arduinoSerial = serial.Serial(self.comPort, 9600)
		arduinoReady = False
		while not arduinoReady:
			if arduinoSerial.read() == "1":
				arduinoReady = True
		  
		arduinoSerial.write("0")
		if arduinoSerial.read() == "1":
			arduinoSerial.write("2")
		self.findPlaneLimits.setEnabled(False)
		self.APSsetupStatus.setText("APS setup completed!")
		self.comPortChoice.setEnabled(False)
		arduinoSerial.close

def main():
	APSprogram = QtWidgets.QApplication(sys.argv)
	window = APSGUI()
	window.show()
	sys.exit(APSprogram.exec_())


if __name__ == "__main__":
	main()