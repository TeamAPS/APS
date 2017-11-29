// Define variables
const int stepPin = 5;
const int directionPin = 6;
const int enablePin = 7;
const int motorSpeed = 1000;

// Setup code; runs once
void setup()
{
  
  // Open serial connection.
  Serial.begin(9600);

  // Define pin modes
  pinMode(stepPin, OUTPUT);
  pinMode(directionPin, OUTPUT);
  pinMode(enablePin, OUTPUT);

  // Print 1 to serial monitor when setup is compelete
  Serial.print('1');
}

// Main program
void loop()
{ 
  // Define variables
  int pythonCommand;
  int numberOfSteps;

  // Initialize motor
  digitalWrite(directionPin, HIGH);
  digitalWrite(enablePin, LOW);  
    
  // Read what's in the serial monitor
  pythonCommand = Serial.read();
  
  // If python is asking for a CW movement
  if(pythonCommand == '0')
  {
    numberOfSteps = Serial.readStringUntil("\n").toInt();
    for(int i = 0; i < numberOfSteps; i++)
    {
       digitalWrite(stepPin, HIGH);
      delayMicroseconds(motorSpeed);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(motorSpeed); 
    }  
    Serial.write('1');
  }
}

