// Open a serial connection and flash LED when input is received

void setup(){
  // Open serial connection.
  Serial.begin(9600);
  pinMode(6, OUTPUT);
  Serial.print('1');
}

void loop(){ 
  int x;
  x = Serial.read();
  if(x == '0'){      // if data present, blink
    digitalWrite(6, HIGH);
    delay(500);            
    digitalWrite(6, LOW);
    delay(500); 
    digitalWrite(6, HIGH);
    delay(500);            
    digitalWrite(6, LOW);
    delay(500);
    digitalWrite(6, HIGH);
    delay(500);            
    digitalWrite(6, LOW);
    delay(500); 
    digitalWrite(6, HIGH);
    delay(500);            
    digitalWrite(6, LOW);
    delay(500);
    Serial.write('1');
  }
  else if (x == '2')
  {
   digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100); 
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100);
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100); 
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100);
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100); 
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100);
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100); 
    digitalWrite(6, HIGH);
    delay(100);            
    digitalWrite(6, LOW);
    delay(100);
    Serial.write('3');
  }
  else{
    digitalWrite(6, HIGH);
    delay(5);            
    digitalWrite(6, LOW);
    delay(5); 
    digitalWrite(6, HIGH);
    delay(5);            
    digitalWrite(6, LOW);
    delay(5);
  }
}

