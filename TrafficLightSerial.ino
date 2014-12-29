
void setup() {
  // initialize serial communication:
  Serial.begin(9600); 
   // initialize the LED pins:
      for (int thisPin = 2; thisPin < 10; thisPin++) {
        pinMode(thisPin, OUTPUT);
      } 
}

void loop() {
  // read the sensor:
  if (Serial.available() > 0) {
    int inByte = Serial.read();
    // do something different depending on the character received.  
    // The switch statement expects single number values for each case;
    // in this exmaple, though, you're using single quotes to tell
    // the controller to get the ASCII value for the character.  For 
    // example 'a' = 97, 'b' = 98, and so forth:

    switch (inByte) {
    case '1':    
      writeLeds(2);
      break;
    case '2':    
      writeLeds(3);
      break;
    case '3':    
      writeLeds(4);
      break;
    case '4':    
      writeLeds(5);
      break;
    case '5':    
      writeLeds(6);
      break;
    case '6':    
      writeLeds(7);
      break;
    case '7':
      writeLeds(8);
      break;
    case '8':
      writeLeds(9);
      break;
    default:
      writeLeds(0);
      break;
    } 
  }
}

void writeLeds(int load) {
  for (int thisPin = 2; thisPin < 10; thisPin++) {
    if (load >= thisPin) {
      digitalWrite(thisPin, HIGH);
    } else {
      digitalWrite(thisPin, LOW);
    }
  }
}
