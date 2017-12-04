// Define variables
const int stepPinY = 5;
const int directionPinY = 6;
const int enablePinY = 7;
const int motorSpeed = 7500;

const int stepPinX = 10;
const int directionPinX = 9;
const int enablePinX = 11;

// Setup code; runs once
void setup()
{
  
  // Open serial connection.
  Serial.begin(9600);

  // Define pin modes
  pinMode(stepPinY, OUTPUT);
  pinMode(directionPinY, OUTPUT);
  pinMode(enablePinY, OUTPUT);
  pinMode(stepPinX, OUTPUT);
  pinMode(directionPinX, OUTPUT);
  pinMode(enablePinX, OUTPUT);

  // Print 1 to serial monitor when setup is compelete
  Serial.print('1');
}

// Main program
void loop()
{ 
  // Define variables
  int pythonCommand, numberOfSteps, directionHighOrLow,
      directionPinRead, stepPinRead;

  // Initialize motor
  digitalWrite(enablePinY, LOW); // Enable pin low: enabled
  digitalWrite(enablePinX, LOW); 
    
  // Read what's in the serial monitor
  pythonCommand = Serial.read();
  
  // If python is asking for a movement
  if(pythonCommand == '0')
  {
    Serial.write('1');
    directionPinRead = Serial.readStringUntil("\n").toInt();
    Serial.write('1');
    directionHighOrLow = Serial.readStringUntil("\n").toInt();
    Serial.write('1');
    digitalWrite(directionPinRead, directionHighOrLow); // Direction low: 
                                          //move towards motors
    numberOfSteps = Serial.readStringUntil("\n").toInt();
    Serial.write('1');
    stepPinRead = Serial.readStringUntil("\n").toInt();
    for(int i = 0; i < numberOfSteps; i++)
    {
      digitalWrite(stepPinRead, HIGH);
      delayMicroseconds(motorSpeed);
      digitalWrite(stepPinRead, LOW);
      delayMicroseconds(motorSpeed); 
    }  
    Serial.write('1');
  }
}

