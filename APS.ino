// Define motor variables
const int stepPinY = 5;
const int directionPinY = 6;
const int stepPinX = 8;
const int directionPinX = 9;
const int stepPinAnemometer = 11;
const int directionPinAnemometer = 12;
const int motorSpeedX = 500;
const int motorSpeedY = 500;
const int motorSpeedAnemometer = 750;

// Define switch variables
const int motorSwitchX = 4;
const int channelSwitchX = 7;
const int motorSwitchY = 2;
const int channelSwitchY = 3;

// Define global variables
int directionPinRead, directionHighOrLow,
    stepPinRead, motorSpeed;
float numberOfSteps;

// Setup code; runs once
void setup()
{  
  // Open serial connection.
  Serial.begin(9600);

  // Define pin modes
  pinMode(stepPinY, OUTPUT);
  pinMode(directionPinY, OUTPUT);
  pinMode(stepPinX, OUTPUT);
  pinMode(directionPinX, OUTPUT);
  pinMode(stepPinAnemometer, OUTPUT);
  pinMode(directionPinAnemometer, OUTPUT);
  pinMode(motorSwitchX, INPUT);
  pinMode(channelSwitchX, INPUT);
  pinMode(motorSwitchY, INPUT);
  pinMode(channelSwitchY, INPUT);

  // Print 1 to serial monitor when setup is compelete
  Serial.print('1');
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) 
  {
      if (data.charAt(i) == separator || i == maxIndex) 
      {
          found++;
          strIndex[0] = strIndex[1] + 1;
          strIndex[1] = (i == maxIndex) ? i+1 : i;
      }
    }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

void setPins()
{
  String incomingDirections;
  Serial.write('1');
  incomingDirections = Serial.readStringUntil("\n");
  directionPinRead = getValue(incomingDirections, ' ', 0).toInt();
  directionHighOrLow = getValue(incomingDirections, ' ', 1).toInt();
  numberOfSteps = getValue(incomingDirections, ' ', 2).toFloat();
  stepPinRead = getValue(incomingDirections, ' ', 3).toInt();

  digitalWrite(directionPinRead, directionHighOrLow); // Direction low: 
                                                      //move towards motors
  if (directionPinRead == directionPinX)
    {
      motorSpeed = motorSpeedX;
    }
  else if (directionPinRead == directionPinY)
    {
      motorSpeed = motorSpeedY;
    }
  else
    {
      motorSpeed = motorSpeedAnemometer;
    }
}

void moveMotors()
{
  digitalWrite(stepPinRead, HIGH);
  delayMicroseconds(motorSpeed);
  digitalWrite(stepPinRead, LOW);
  delayMicroseconds(motorSpeed);
}

// Main program
void loop()
{ 
  // Define variables
  int pythonCommand;
  float xStepCounter = 0.0, yStepCounter = 0.0;
    
  // Read what's in the serial monitor
  pythonCommand = Serial.read();
  
  // If python is asking for calibration
  if(pythonCommand == '0')
  {
    setPins();
    for(float i = 0.0; i < numberOfSteps; i++)
    {
      if(directionPinRead == directionPinX)
      {
        if (digitalRead(motorSwitchX) == LOW || digitalRead(channelSwitchX) == LOW)
        {
          Serial.println(String(xStepCounter));
          i = numberOfSteps + 1.0;
        }
        else
        {
          moveMotors();
          xStepCounter++;
        }
      }
      else if (directionPinRead == directionPinY)
      {
        if (digitalRead(motorSwitchY) == LOW || digitalRead(channelSwitchY) == LOW)
        {
          Serial.println(String(yStepCounter));
          i = numberOfSteps + 1.0;
        }
        else
        {
          moveMotors();
          yStepCounter++;
        }
      }  
    }  
  }
  
  // If python is asking for a normal movement
  else if(pythonCommand == '1')
  {
    setPins();
    for(float i = 0.0; i < numberOfSteps; i++) 
    {
      moveMotors();
    }
    Serial.write('1');
  }
}

