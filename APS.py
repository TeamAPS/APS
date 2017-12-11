import os
import sys
import serial
from PyQt5 import QtWidgets, uic
import serial.tools.list_ports
import math

# Create a list of the used serial ports

availableSerialPorts = serial.tools.list_ports.comports()

# Read and use the .ui file
qtCreatorFile = "APS.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# GUI class 
class APSGUI(QtWidgets.QMainWindow, Ui_MainWindow):
	
	# Class initialization
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.dataPathBox.setText("No File Selected")
		self.findPlaneLimits.setEnabled(False)
		self.xOperationChoice.setEnabled(False)
		self.yOperationChoice.setEnabled(False)
		self.timeOperationChoice.setEnabled(False)
		self.operationStart.setEnabled(False)
		self.arduinoSerial = None
		self.dataFilePath = None
		self.xRange = None # steps
		self.yRange = None # steps
		self.currentX = None # steps
		self.currentY = None # steps
		self.anemometerExtension = 20.0 # inches. Must be fixed by user
		
		# Populate the COM port list
		self.comPortChoice.addItem("No Port Selected")
		for serialPort in availableSerialPorts:
			self.comPortChoice.addItem(str(serialPort))
			
		# Buttons and dependencies
		self.comPortChoice.currentIndexChanged.connect(self.connectArduino)
		self.findPlaneLimits.clicked.connect(self.getLimits)
		self.dataPathBrowse.clicked.connect(self.selectDataPath)
		self.dataPathBox.textChanged.connect(self.updateDataPath)
		self.manualModeRadio.clicked.connect(self.modeChanged)
		self.autoModeRadio.clicked.connect(self.modeChanged)
		self.xOperationChoice.textChanged.connect(self.enableStart)
		self.yOperationChoice.textChanged.connect(self.enableStart)
		self.timeOperationChoice.textChanged.connect(self.enableStart)
		self.operationStart.clicked.connect(self.startAPS)
		
	def connectArduino(self):
		# The first space is where the port name ends
		comPort = self.comPortChoice.currentText().partition(" ")[0]
		if comPort.startswith("COM"):
			# Baud rate is 9600
			self.arduinoSerial = serial.Serial(comPort, 9600)
			arduinoReady = False
			while not arduinoReady:
				if self.arduinoSerial.read() == "1":
					arduinoReady = True
			self.findPlaneLimits.setEnabled(True)
		else:
			arduinoSerial = None
			self.findPlaneLimits.setEnabled(False)
	
	def getLimits(self):
		# For y: CCW moves the carriage towards motors
		# For x: CW moves the carriage towards motor

		# Calibrate Y
		# Go all the way to the bottom
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("y","CCW", self.toSteps(100), True)
		
		# Go 100 steps up to clear the switch
		self.moveMotor("y","CW", 100.0)
		
		# Go all the way to the top
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("y","CW", self.toSteps(100), True)
		
		# Go 100 steps down to clear the switch
		self.moveMotor("y","CCW", 100.0)
		
		# Calibrate X
		# Go all the way to the right
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("x","CW", self.toSteps(100), True)
		
		# Go 100 steps to the left to clear the switch
		self.moveMotor("x","CCW", 100.0)
		
		# Go all the way to the left
		# Move 100 inches to ensure hitting the switch
		movementDone = self.moveMotor("x","CCW", self.toSteps(100), True)
		
		# Go 100 steps to the right to clear the switch
		self.moveMotor("x","CW", 100.0)
		
		# Set where the anemometer currently is
		self.currentX = self.xRange
		self.currentY = self.yRange
		
		# Don't forget to add the 100 steps to the current ranges
		self.xRange = self.xRange + 100.0
		self.yRange = self.yRange + 100.0 
    
		if movementDone:
			self.findPlaneLimits.setEnabled(False)
			self.APSsetupStatus.setText("APS Setup Completed!")
			self.comPortChoice.setEnabled(False)
			self.maximumXlabel.setText("Maximum X:" + str(round(self.toInches(self.xRange), 3) \
			+ self.anemometerExtension) + "in.")
			self.maximumYlabel.setText("Maximum Y:" + str(round(self.toInches(self.yRange), 3) \
			+ self.anemometerExtension) + "in.")
			self.currentXlabel.setText("Current X:" + str(round(self.toInches(self.currentX), \
			3)) + "in.")
			self.currentYlabel.setText("Current Y:" + str(round(self.toInches(self.currentY), \
			3)) + "in.")
		
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
			
	def moveMotor(self, motorAxis, direction, steps, calibrationFlag = None):
		
		directionPinX = "9"
		directionPinY = "6"
		directionPinAnemometer = "12"
		stepPinX = "8"
		stepPinY = "5"
		stepPinAnemometer = "11"
		
		if motorAxis == "x":
			directions = {"CW":[directionPinX, "1"],
				"CCW": [directionPinX, "0"]}
		elif motorAxis == "y":
			directions = {"CW":[directionPinY, "1"],
				"CCW": [directionPinY, "0"]}
		else:
			directions = {"CW":[directionPinAnemometer, "1"],
				"CCW": [directionPinAnemometer, "0"]}
		
		axes = {"x": stepPinX, "y": stepPinY, "a": stepPinAnemometer}
		
		if calibrationFlag == None:
			self.arduinoSerial.write("1\n")
		else:
			self.arduinoSerial.write("0\n")
		
		if self.arduinoSerial.read() == "1":
			self.arduinoSerial.write(directions[direction][0]+ " " + \
			directions[direction][1] + " " + str(steps) + " " + \
			axes[motorAxis] + "\n")	

		if calibrationFlag == None:
			if self.arduinoSerial.read() == "1":
				self.arduinoSerial.close
				return True
		else:
			numberOfSteps = float(self.arduinoSerial.readline())
			
			if motorAxis == "x":
					self.xRange = numberOfSteps
					return True
			else:
				self.yRange = numberOfSteps
				return True
			
	def modeChanged(self):
		self.operationStart.setEnabled(False)
		self.xOperationChoice.setText("")
		self.yOperationChoice.setText("")
		self.timeOperationChoice.setText("")
		
		if self.manualModeRadio.isChecked():
			self.xOperationLabel.setText("X Position (in.):")
			self.yOperationLabel.setText("Y Position (in.):")
			self.timeOperationLabel.setText("Measurement Time (sec.):")
		
		if self.autoModeRadio.isChecked():
			self.xOperationLabel.setText("Number of X Positions:")
			self.yOperationLabel.setText("Number of Y Positions:")
			self.timeOperationLabel.setText("Individual Measurement Time (sec.):")
		
		self.xOperationChoice.setEnabled(True)
		self.yOperationChoice.setEnabled(True)
		self.timeOperationChoice.setEnabled(True)
		
	def enableStart(self):
		self.operationModeStatus.setText("Operation Not Set Up")
		self.operationStart.setEnabled(False)
		
		if self.manualModeRadio.isChecked() and \
		self.xOperationChoice.displayText().\
		replace('.','',1).isdigit()	and self.yOperationChoice.\
		displayText().replace('.','',1).isdigit() and \
		self.timeOperationChoice.displayText().replace('.','',1).isdigit():
				self.operationModeStatus.setText("Operation Set Up!")
				self.operationStart.setEnabled(True)
		
		if self.autoModeRadio.isChecked() and \
		self.xOperationChoice.displayText().isdigit() and \
		self.yOperationChoice.displayText().isdigit() and \
		self.timeOperationChoice.displayText().replace('.','',1).isdigit():
				self.operationModeStatus.setText("Operation Set Up!")
				self.operationStart.setEnabled(True)
				
	def startAPS(self):
		if self.APSsetupStatus.text().endswith("!") \
		and self.dataPathStatus.text().endswith("!"):
			if self.manualModeRadio.isChecked():
				return True # put APS go! manual code here
			else:
				return True # call self.calculateDataPoints here

		elif self.APSsetupStatus.text().endswith("!"):
			QtWidgets.QMessageBox.warning(self, "APS Error", str(self.dataPathStatus.text()))
		elif self.dataPathStatus.text().endswith("!"):
			QtWidgets.QMessageBox.warning(self, "APS Error", str(self.APSsetupStatus.text()))
		else:
			QtWidgets.QMessageBox.warning(self, "APS Error", str(self.APSsetupStatus.text()) + \
			"\n" + str(self.dataPathStatus.text()))
			
	def toInches(self, steps):
		pulleyDiameter = 0.955 # Inches
		stepsPerRevolution = 1600.0 # Set by the motor drivers 
		revolution = math.pi * pulleyDiameter
		conversionFactor = stepsPerRevolution / revolution
		inInches = (1.0  /conversionFactor) * steps
		return inInches
		
	def toSteps(self, inches):
		pulleyDiameter = 0.955 # Inches
		stepsPerRevolution = 1600.0 # Set by the motor drivers 
		revolution = math.pi * pulleyDiameter
		conversionFactor = stepsPerRevolution / revolution
		inSteps = conversionFactor * inches
		return math.floor(inSteps)
		
		

def main():
	APSprogram = QtWidgets.QApplication(sys.argv)
	window = APSGUI()
	window.show()
	sys.exit(APSprogram.exec_())


if __name__ == "__main__":
	main()