import os
import sys
import serial
import time
import datetime
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
		self.ySlider.setEnabled(False)
		self.xSlider.setEnabled(False)
		self.manualModeRadio.setEnabled(False)
		self.autoModeRadio.setEnabled(False)
		self.arduinoSerial = None
		self.dataFilePath = None
		self.xRange = None # steps
		self.yRange = None # steps
		self.currentX = None # steps
		self.currentY = None # steps
		self.topClearance = None #inches
		self.bottomClearance = None #inches
		self.leftClearance = None #inches
		self.rightClearance = None #inches
		self.anemometerExtension = 10.75 # inches
		
		# Must be fixed by user - Distance from tip to motor axis
		self.topAngleRot = math.radians(120) # Angles to reach top corners
		self.botAngleRot = math.radians(35) # Angles to reach bottom corners
		self.yUp = "CW"
		self.yDown = "CCW"
		self.xLeft = "CCW"
		self.xRight = "CW"
		
		
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
		self.aboutOption.triggered.connect(self.aboutPopup)
		self.configureAPSoption.triggered.connect(self.configureAPS)
		self.xSlider.valueChanged.connect(self.xSliderChanged)
		self.ySlider.valueChanged.connect(self.ySliderChanged)
		
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
		# Go all the way to the top
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("y",self.yUp, self.toSteps(100), True)
		
		# Go .25 in steps down to clear the switch
		self.moveMotor("y", self.yDown, self.toSteps(0.25))
		
		# Go all the way to the bottom
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("y", self.yDown, self.toSteps(100), True)
		
		# Go .25 in up to clear the switch
		self.moveMotor("y", self.yUp, self.toSteps(0.25))
		
		# Calibrate X
		# Go all the way to the right
		# Move 100 inches to ensure hitting the switch
		self.moveMotor("x", self.xRight, self.toSteps(100), True)
		
		# Go .25 in to the left to clear the switch
		self.moveMotor("x", self.xLeft, self.toSteps(0.25))
		
		# Go all the way to the left
		# Move 100 inches to ensure hitting the switch
		movementDone = self.moveMotor("x", self.xLeft, self.toSteps(100), True)
		
		# Go .25 in to the right to clear the switch
		self.moveMotor("x", self.xRight, self.toSteps(0.25))
		
		# Set where the anemometer currently is
		self.currentX = self.xRange
		self.currentY = self.yRange
		
		# Don't forget to add the .25 in to the current ranges
		self.xRange = self.xRange + self.toSteps(0.25)
		self.yRange = self.yRange + self.toSteps(0.25) 
    
		if movementDone:
			self.findPlaneLimits.setEnabled(False)
			self.APSsetupStatus.setText("APS Setup Completed!")
			self.comPortChoice.setEnabled(False)
			self.maximumXlabel.setText("Maximum X:" + str(round(self.toInches(self.xRange), 1) \
			+ self.anemometerExtension) + " in.")
			self.maximumYlabel.setText("Maximum Y:" + str(round(self.toInches(self.yRange), 1) \
			+ self.anemometerExtension) + " in.")
			self.currentXlabel.setText("Current X:" + str(round(self.toInches(self.currentX), \
			1)) + " in.")
			self.currentYlabel.setText("Current Y:" + str(round(self.toInches(self.currentY), \
			1)) + " in.")
			self.manualModeRadio.setEnabled(True)
			self.autoModeRadio.setEnabled(True)
			self.xSlider.setMinimum(0)
			self.xSlider.setMaximum(int(self.xRange))
			self.ySlider.setMinimum(0)
			self.ySlider.setMaximum(int(self.yRange))
		
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
			file = open(self.dataFilePath, 'a')
			headers = "No.			Date and Time			X Position (in.)			Y Position (in.)\n"
			file.write(headers)
			file.close()
	
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
				file = open(self.dataFilePath, 'a')
				headers = "No.			Date and Time			X Position (in.)			Y Position (in.)\n"
				file.write(headers)
				file.close()
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
			directions = {"CW":[directionPinAnemometer, "0"],
				"CCW": [directionPinAnemometer, "1"]}

		axes = {"x": stepPinX, "y": stepPinY, "a": stepPinAnemometer}
		if calibrationFlag == None:
			self.arduinoSerial.write("1\n")
		elif calibrationFlag == '2':
			self.arduinoSerial.write("2\n")
		else:
			self.arduinoSerial.write("0\n")
		
		if self.arduinoSerial.read() == "1":
			self.arduinoSerial.write(directions[direction][0]+ " " + \
			directions[direction][1] + " " + str(steps) + " " + \
			axes[motorAxis] + "\n")	
		if calibrationFlag == None or calibrationFlag == "2":
			if self.arduinoSerial.read() == "1":
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
		self.operationStart.setEnabled(True)
		self.xSlider.setEnabled(False)
		self.ySlider.setEnabled(False)
		self.xSlider.setValue(0)
		self.ySlider.setValue(0)
		self.xOperationChoice.setText("")
		self.yOperationChoice.setText("")
		self.timeOperationChoice.setText("")
		
		if self.manualModeRadio.isChecked():
			self.operationStart.setEnabled(False)
			self.xOperationLabel.setText("X Position (in.):")
			self.yOperationLabel.setText("Y Position (in.):")
			self.timeOperationLabel.setText("Measurement Time (sec.):")
			self.xSlider.setEnabled(True)
			self.ySlider.setEnabled(True)
			self.xOperationChoice.setEnabled(True) #remove after design show
			self.yOperationChoice.setEnabled(True) #remove after design show
			self.timeOperationChoice.setEnabled(True) #remove after design show
		
		if self.autoModeRadio.isChecked():
			self.operationStart.setEnabled(True) #remove after design show
			self.xOperationLabel.setText("Number of X Positions:")
			self.yOperationLabel.setText("Number of Y Positions:")
			self.timeOperationLabel.setText("Individual Measurement Time (sec.):")
			self.xOperationChoice.setText(" ") #remove after design show
			self.xOperationChoice.setEnabled(False) #remove after design show
			self.yOperationChoice.setEnabled(False) #remove after design show
			self.timeOperationChoice.setEnabled(False) #remove after design show
		
		# Commented out for design show
		#self.xOperationChoice.setEnabled(True)
		#self.yOperationChoice.setEnabled(True)
		#self.timeOperationChoice.setEnabled(True)
			
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
		
		# Commented out for design show
		if self.autoModeRadio.isChecked():# and \
		#self.xOperationChoice.displayText().isdigit() and \
		#self.yOperationChoice.displayText().isdigit() and \
		#self.timeOperationChoice.displayText().replace('.','',1).isdigit():
			self.operationModeStatus.setText("Operation Set Up!")
			self.operationStart.setEnabled(True)
				
	def startAPS(self):
		if self.APSsetupStatus.text().endswith("!"):
		#and self.dataPathStatus.text().endswith("!"):
			if self.manualModeRadio.isChecked():
				self.manualMove()
			else:
				ensureMsg = "Are you sure you want enter Auto Mode? Is the anemometer in the down position?"
				reply = QtWidgets.QMessageBox.question(self, 'Auto Mode', \
				ensureMsg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
				if reply == QtWidgets.QMessageBox.No:
					return False
				else:
					try:
						self.autoMove()
					except Exception as e:
						print(e)
		else:
		#elif self.APSsetupStatus.text().endswith("!"):
			QtWidgets.QMessageBox.warning(self, "APS Error", str(self.APSsetupStatus.text()))
		#elif self.dataPathStatus.text().endswith("!"):
			#QtWidgets.QMessageBox.warning(self, "APS Error", str(self.APSsetupStatus.text()))
		#else:
			#QtWidgets.QMessageBox.warning(self, "APS Error", str(self.APSsetupStatus.text()) + \
			#"\n" + str(self.dataPathStatus.text()))
			
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
		

	def aboutPopup(self):
		QtWidgets.QMessageBox.about(self, "About APS", "Anemometer "
		"Positioning Device (APS)\n\nDesigned and programmed by Team"
		" APS:\nHashim Al Lawati - allaw009@umn.edu\nSyed Farhan Abid"
		" - abidx011@umn.edu\nAdam Jenson - jenso081@umn.edu\n"
		"Matthew Albers - alber433@umn.edu\nMaxwell Fite - "
		"fitex005@umn.edu\n\nUniversity of Minnesota\nME4054W - "
		"Fall 2017\n\nProject Advisor:\nNicholas Hugh\nDaikin Applied"
		"\nnicholas.hugh@daikinapplied.com")
		
	def xSliderChanged(self):
		self.xOperationChoice.setText(str(round( \
		self.toInches(self.xSlider.value()), 1)))
	
	def ySliderChanged(self):
		self.yOperationChoice.setText(str(round( \
		self.toInches(self.ySlider.value()), 1)))
      
	def autoMove(self):
		self.moveMotor("a","CCW",1600)
		
	def configureAPS(self):
		QtWidgets.QMessageBox.information(self, "APS Configuration", str("hello"), \
		QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
		
		#make these variables later, and add .25 for clearing the switches
		self.topClearance = 6 + 0.25
		self.bottomClearance = 6 + 0.25
		self.leftClearance = 10 + 0.25 #to motor shaft
		self.rightClearance = 6 + 0.25
		
		
	def manualMove(self):
		xSpan = self.leftClearance + self.toInches(self.xRange) + self.rightClearance
		ySpan = self.bottomClearance + self.toInches(self.yRange) + self.topClearance
		xDesired = float(self.xOperationChoice.displayText())
		yDesired = float(self.yOperationChoice.displayText())
		
		if yDesired > (ySpan / 2):
			if xDesired < self.leftClearance:
				deltaX = self.leftClearance - xDesired
				angle = math.acos(deltaX / self.anemometerExtension)
				yCompensation = self.anemometerExtension * (1 - math.sin(angle))
				anemometerSteps = 1600.0 * ( (3 * math.pi / 2) - angle) / (2 * math.pi)
				
				self.moveMotor("a","CCW", anemometerSteps)
				self.moveMotor("y",self.yUp, self.toSteps(yDesired \
				- self.anemometerExtension + yCompensation - \
				self.bottomClearance - 3.5))
				
				time.sleep(float(self.timeOperationChoice.displayText()))
				
				self.moveMotor("y",self.yDown, self.toSteps(100), "2")
				self.moveMotor("y", self.yUp, self.toSteps(0.25))
				self.moveMotor("x", self.xLeft, self.toSteps(100), "2")
				self.moveMotor("x", self.xRight, self.toSteps(0.25))
				self.moveMotor("a","CW", anemometerSteps)
				
			
		
		

def main():
	APSprogram = QtWidgets.QApplication(sys.argv)
	window = APSGUI()
	window.show()
	sys.exit(APSprogram.exec_())


if __name__ == "__main__":
	main()