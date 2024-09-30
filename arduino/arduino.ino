#include <SoftwareSerial.h>

#define RIGHT_MOTOR_PIN1 2
#define RIGHT_MOTOR_PIN2 3
#define LEFT_MOTOR_PIN1 4
#define LEFT_MOTOR_PIN2 5
#define BUZZER_PIN 6
#define WHITE_LED_PIN 8
#define RED_LED_PIN 10
#define RIGHT_INDICATOR_PIN 7
#define LEFT_INDICATOR_PIN 9

#define BLUETOOTH_RX A0
#define BLUETOOTH_TX A1






SoftwareSerial bluetooth(BLUETOOTH_RX, BLUETOOTH_TX); // RX, TX

void setup() {
  
  pinMode(RIGHT_MOTOR_PIN1, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN2, OUTPUT);
  pinMode(LEFT_MOTOR_PIN1, OUTPUT);
  pinMode(LEFT_MOTOR_PIN2, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(WHITE_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(RIGHT_INDICATOR_PIN, OUTPUT);
  pinMode(LEFT_INDICATOR_PIN, OUTPUT);
  
  Serial.begin(9600);
  bluetooth.begin(9600);
}

void loop() {
  if (bluetooth.available()) {
    String command = bluetooth.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String command) {
  command.trim();
  String action = command;
  Serial.println(command);
  if (action=="1") {
    moveForward();
  } else if (action=="2") {
    moveBackward();
  } else if (action=="3") {
    turnRight();
  } else if (action=="4") {
    turnLeft();
  } else if (action == "5") {
    digitalWrite(WHITE_LED_PIN, HIGH);
  } else if (action == "6") {
    digitalWrite(WHITE_LED_PIN, LOW);
  }
  else if(action=="0"){
    stopMotors();
  }
}

void moveForward() {
  digitalWrite(LEFT_MOTOR_PIN1, LOW);
  digitalWrite(LEFT_MOTOR_PIN2, HIGH);
  digitalWrite(RIGHT_MOTOR_PIN1, HIGH);
  digitalWrite(RIGHT_MOTOR_PIN2, LOW);
}

void moveBackward() {
  digitalWrite(LEFT_MOTOR_PIN1, HIGH);
  digitalWrite(LEFT_MOTOR_PIN2, LOW);
  digitalWrite(RIGHT_MOTOR_PIN1, LOW);
  digitalWrite(RIGHT_MOTOR_PIN2, HIGH);
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  
}

void turnRight() {
  digitalWrite(RIGHT_MOTOR_PIN1, HIGH);
  digitalWrite(RIGHT_MOTOR_PIN2, LOW);
  digitalWrite(LEFT_MOTOR_PIN1, HIGH);
  digitalWrite(LEFT_MOTOR_PIN2, LOW);
  digitalWrite(RIGHT_INDICATOR_PIN, HIGH);
}


void turnLeft() {
  digitalWrite(RIGHT_MOTOR_PIN1, LOW);
  digitalWrite(RIGHT_MOTOR_PIN2, HIGH);
  digitalWrite(LEFT_MOTOR_PIN1, LOW);
  digitalWrite(LEFT_MOTOR_PIN2, HIGH);
  digitalWrite(LEFT_INDICATOR_PIN, HIGH);
    
}
void stopMotors() {
  digitalWrite(RIGHT_MOTOR_PIN1, LOW);
  digitalWrite(RIGHT_MOTOR_PIN2, LOW);
  digitalWrite(LEFT_MOTOR_PIN1, LOW);
  digitalWrite(LEFT_MOTOR_PIN2, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LEFT_INDICATOR_PIN, LOW);
  digitalWrite(RIGHT_INDICATOR_PIN, LOW);
}
