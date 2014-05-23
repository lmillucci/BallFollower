String inData;
int val[3];
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
            val[i]=inData.toInt();
            i++;

            if(inData == "+++\n"){ // DON'T forget to add "\n" at the end of the string.
              //Serial.println("OK. Press h for help.");
            }   

            if(i==3){
              if(val[0]==8){
                forward(val[1]);
              }
              else if(val[0]==4){
                right(val[1]);
              }else if(val[0]==6){
                left(val[1]);
              }else if(val[0] == 5){
                changeSpeed(val[1], val[2]);
              }
              

              i=0;
              //Serial.print(value);
              Serial.flush();
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
}  

void changeSpeed(int left,int right){
   digitalWrite(12, LOW);  //Establishes backward direction of Channel A
   digitalWrite(9, LOW);   //Disengage the Brake for Channel A
   digitalWrite(13, HIGH); //Establishes forward direction of Channel B
   digitalWrite(8, LOW);   //Disengage the Brake for Channel B
   int value_left, value_right;
   value_left=(left*255)/100;
   value_right=(right*255)/100;
   analogWrite(3, value_left);
   analogWrite(11, value_right); 
}
   



