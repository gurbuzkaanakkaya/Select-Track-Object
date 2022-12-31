

#include <Servo.h>
int data_x1 = 0;
int data[1];
Servo myservo_x1;
Servo myservo_y1;




void setup() {
  Serial.begin(9600);
  pinMode(MotorL1, OUTPUT);
  myservo_x1.attach(9);
  myservo_y1.attach(10);
  myservo_x1.write(90);
  myservo_y1.write(90);
}

void loop() {
 while (Serial.available() >= 2) {
     for (int i = 0; i < 2; i++) {
      data[i] = Serial.read();
     }
      myservo_x1.write(data[0]);
      myservo_y1.write(data[1]);
      Serial.println(data[0]);
      Serial.println(data[1]);
 }
}
