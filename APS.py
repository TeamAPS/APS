import os
import sys
import serial
from PyQt5 import QtWidgets, uic
import serial.tools.list_ports
import time

# Create a list of the used serial ports

availableSerialPorts = serial.tools.list_ports.comports()

##############################################################

# Read and use the .ui file
qtCreatorFile = "APS.ui"
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class APSGUI(QtWidgets.QMainWindow, Ui_MainWindow):
	
	# Class intialization
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.dataPathBox.setText("No File Selected")
		self.findPlaneLimits.setEnabled(False)
		self.comPort = None
		self.dataFilePath = None
		
		# Populate the COM port list
		self.comPortChoice.addItem("No Port Selected")
		for serialPort in availableSerialPorts:
			self.comPortChoice.addItem(str(serialPort))
			
		# Buttons and dependencies
		self.comPortChoice.currentIndexChanged.connect(self.connectArduino)
		self.findPlaneLimits.clicked.connect(self.getLimits)
		self.dataPathBrowse.clicked.connect(self.selectDataPath)
		self.dataPathBox.textChanged.connect(self.updateDataPath)
	
	
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
		
		arduinoSerial.write("0\n")
		arduinoSerial.write("400\n")
		
		
		if arduinoSerial.read() == "1":
			self.findPlaneLimits.setEnabled(False)
			self.APSsetupStatus.setText("APS Setup Completed!")
			self.comPortChoice.setEnabled(False)
		arduinoSerial.close
		
	def selectDataPath(self):
		# The first item in the tuple is the file path needed
		filePath = QtWidgets.QFileDialog.getSaveFileName(self,
			'Data File Location', os.getcwd(), filter='*.txt')[0]
		# Make sure user chose a file
		if not filePath == '':
			# If chosen file doesn't exist, create it
			if not os.path.isfile(filePath):
				open(filePath, 'a').close()
			self.dataPathStatus.setText("Data File Selected!")
			self.dataFilePath = filePath
			self.dataPathBox.setText(filePath)
	
	def updateDataPath(self):
		filePath = self.dataPathBox.displayText()
		# Make sure user chose a correct file
		if filePath.endswith(".txt"):
			# Try to create the file if it doesn't exist
			try:
				if not os.path.isfile(filePath):
					open(filePath, 'a').close()
				self.dataPathStatus.setText("Data File Selected!")
				self.dataFilePath = filePath
				self.dataPathBox.setText(filePath)
			# If you get an error, it means the path isn't valid
			except:
				self.dataPathStatus.setText("Please Select a Valid File")
				self.dataFilePath = None
		else:
			self.dataPathStatus.setText("Please Select a Valid File")
			self.dataFilePath = None
			
				
	
		

def main():
	APSprogram = QtWidgets.QApplication(sys.argv)
	window = APSGUI()
	window.show()
	sys.exit(APSprogram.exec_())


if __name__ == "__main__":
	main()