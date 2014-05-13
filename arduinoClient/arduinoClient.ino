String inData;
int val[2];
int i=0;
int j;

void setup() {
    Serial.begin(9600);
    //Serial.println("Serial conection started, waiting for instructions...");
    
    //Setup Channel A
    pinMode(12, OUTPUT); //Initiates Motor Channel A pin
    pinMode(9, OUTPUT); //Initiates Brake Channel A pin
  
    //Setup Channel B
    pinMode(13, OUTPUT); //Initiates Motor Channel A pin
    pinMode(8, OUTPUT);  //Initiates Brake Channel A pin
    
}

void loop() {
    while (Serial.available() > 0)
    {
        char recieved = Serial.read();
        inData += recieved; 

        // Process message when new line character is recieved
        if (recieved == '\n')
        {
            //Serial.print("Arduino Received: ");
            //Serial.print(inData);
            val[i]=inData.toInt();
            i++;

            // You can put some if and else here to process the message juste like that:

            if(inData == "+++\n"){ // DON'T forget to add "\n" at the end of the string.
              //Serial.println("OK. Press h for help.");
            }   

            if(i==2){
              if(val[0]==8){
                forward(val[1]);
              }
              else if(val[0]==4){
                right(val[1]);
              }else if(val[0]==6){
                left(val[1]);
              }
              
              /*Serial.print(val[0]);
              Serial.print("\n");
              Serial.print(val[1]);
              Serial.print("\n");
              Serial.print("-------");
              Serial.print("\n");*/

              i=0;
            }
            inData = ""; // Clear recieved buffer
            //delay(200);
        }
    }
}

void forward(int u){
   digitalWrite(12, LOW);  //Establishes backward direction of Channel A
   digitalWrite(9, LOW);   //Disengage the Brake for Channel A
   digitalWrite(13, HIGH); //Establishes forward direction of Channel B
   digitalWrite(8, LOW);   //Disengage the Brake for Channel B
   int value;
   value=(u*255)/100;
   analogWrite(3, value);
   analogWrite(11, value); 
  
  // Serial.print(value); 
   
}

void left(int u){
   digitalWrite(12, LOW);  //Establishes backward direction of Channel A
   digitalWrite(9, LOW);   //Disengage the Brake for Channel A
   digitalWrite(13, LOW); //Establishes forward direction of Channel B
   digitalWrite(8, LOW);   //Disengage the Brake for Channel B
   int value;
   value=(u*255)/100;
   analogWrite(3, value);
   analogWrite(11, value); 
   
   //Serial.print(value);
}

void right(int u){
   digitalWrite(12, HIGH);  //Establishes backward direction of Channel A
   digitalWrite(9, LOW);   //Disengage the Brake for Channel A   digitalWrite(13, HIGH); //Establishes forward direction of Channel B
   digitalWrite(8, LOW);   //Disengage the Brake for Channel B
   int value;
   value=(u*255)/100;
   analogWrite(3, value);
   analogWrite(11, value); 
   
   //Serial.print(value);
   Serial.flush();
}
