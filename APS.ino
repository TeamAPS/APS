// Define motor variables
const int stepPinY = 5;
const int directionPinY = 6;
const int stepPinX = 8;
const int directionPinX = 9;
const int stepPinAnemometer = 11;
const int directionPinAnemometer = 12;
const int motorSpeedX = 500;
const int motorSpeedY = 500;
const int motorSpeedAnemometer = 500;

// Define switch variables
const int motorSwitchX = 0;
const int channelSwitchX = 1;
const int motorSwitchY = 2;
const int channelSwitchY = 3;

// Define global variables
int directionPinRead, directionHighOrLow,
    numberOfSteps, stepPinRead, motorSpeed;

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
  pinMode(motorSwitchX, OUTPUT);
  pinMode(channelSwitchX, OUTPUT);
  pinMode(motorSwitchY, OUTPUT);
  pinMode(channelSwitchY, OUTPUT);

  // Print 1 to serial monitor when setup is compelete
  Serial.print('1');
}

void setPins()
{
  Serial.write('1');
  directionPinRead = Serial.readStringUntil("\n").toInt();
  Serial.write('1');
  directionHighOrLow = Serial.readStringUntil("\n").toInt();
  Serial.write('1');
  numberOfSteps = Serial.readStringUntil("\n").toInt();
  Serial.write('1');
  stepPinRead = Serial.readStringUntil("\n").toInt();

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
  int pythonCommand, xStepCounter = 0, yStepCounter = 0;
    
  // Read what's in the serial monitor
  pythonCommand = Serial.read();
  
  // If python is asking for calibration
  if(pythonCommand == '0')
  {
    setPins();
    for(int i = 0; i < numberOfSteps; i++)
    {
      if (digitalRead(motorSwitchX) == HIGH || digitalRead(channelSwitchX) == HIGH
        || digitalRead(motorSwitchY) == HIGH || digitalRead(channelSwitchY) == HIGH)
       {
          if (directionPinRead == directionPinX)
        {
          Serial.println(String(xStepCounter) + "\n");
        }
        else if (directionPinRead == directionPinY)
        {
          Serial.println(String(yStepCounter) + "\n");
        }
       }
      else
      {
        moveMotors();
        if (directionPinRead == directionPinX)
        {
          xStepCounter++;
        }
        else if (directionPinRead == directionPinY)
        {
          yStepCounter++;
        }
      }  
    }
  }
  
  // If python is asking for a normal movement
  else if(pythonCommand == '1')
  {
    setPins();
    for(int i = 0; i < numberOfSteps; i++) 
    {
      moveMotors();
    }
    Serial.write('1');
  }
}

