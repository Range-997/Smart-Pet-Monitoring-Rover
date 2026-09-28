// Smart Pet Monitoring Rover - Arduino Uno firmware
// Final wiring used in the prototype:
// ENA D5, ENB D6, IN1 D8, IN2 D9, IN3 D10, IN4 D11
// HC-SR04: TRIG D12, ECHO D13
// Left IR OUT A0, Right IR OUT A1

const int ENA = 5;
const int ENB = 6;
const int IN1 = 8;
const int IN2 = 9;
const int IN3 = 10;
const int IN4 = 11;

const int IR_LEFT_PIN = A0;
const int IR_RIGHT_PIN = A1;
const int TRIG_PIN = 12;
const int ECHO_PIN = 13;

const int SPEED_FORWARD = 95;
const int SPEED_TURN = 95;
const int STOP_DISTANCE_CM = 20;
const bool IR_OBSTACLE_STATE = LOW;

char currentCmd = 'S';
bool autoMode = false;
int lastAvoidTurn = 1;
unsigned long lastSensorCheck = 0;

void setup() {
  Serial.begin(9600);

  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(IR_LEFT_PIN, INPUT);
  pinMode(IR_RIGHT_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  stopCar();
  Serial.println("Rover ready: F/B/L/R/S, A=auto, M=manual");
}

void loop() {
  if (Serial.available() > 0) {
    char received = Serial.read();
    handleCommand(received);
  }

  if (autoMode && millis() - lastSensorCheck > 120) {
    lastSensorCheck = millis();
    checkObstacleResponse();
  }
}

void handleCommand(char c) {
  c = toupper(c);

  if (c == 'A') {
    autoMode = true;
    currentCmd = 'S';
    stopCar();
    Serial.println("Auto mode");
    return;
  }

  if (c == 'M') {
    autoMode = false;
    currentCmd = 'S';
    stopCar();
    Serial.println("Manual mode");
    return;
  }

  if (c == 'F' || c == 'B' || c == 'L' || c == 'R' || c == 'S') {
    currentCmd = c;
    executeCommand(currentCmd);
  }
}

void executeCommand(char c) {
  if (c == 'F') forwardCar();
  else if (c == 'B') backwardCar();
  else if (c == 'L') leftTurn();
  else if (c == 'R') rightTurn();
  else stopCar();
}

void checkObstacleResponse() {
  bool leftBlocked = digitalRead(IR_LEFT_PIN) == IR_OBSTACLE_STATE;
  bool rightBlocked = digitalRead(IR_RIGHT_PIN) == IR_OBSTACLE_STATE;
  float frontDistance = readDistanceCM();
  bool frontBlocked = frontDistance > 0 && frontDistance < STOP_DISTANCE_CM;

  if (!leftBlocked && !rightBlocked && !frontBlocked) {
    executeCommand(currentCmd);
    return;
  }

  stopCar();
  delay(120);

  if (frontBlocked && rightBlocked && !leftBlocked) {
    leftTurn();
    delay(450);
  } else if (frontBlocked && leftBlocked && !rightBlocked) {
    rightTurn();
    delay(450);
  } else if (frontBlocked && !leftBlocked && !rightBlocked) {
    if (lastAvoidTurn > 0) {
      rightTurn();
      lastAvoidTurn = -1;
    } else {
      leftTurn();
      lastAvoidTurn = 1;
    }
    delay(420);
  } else if (leftBlocked && !rightBlocked) {
    rightTurn();
    delay(300);
  } else if (rightBlocked && !leftBlocked) {
    leftTurn();
    delay(300);
  }

  stopCar();
  delay(80);
}

float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 25000UL);
  if (duration == 0) return -1;

  float distance = duration * 0.0343 / 2.0;
  return distance;
}

void setSpeed(int leftSpeed, int rightSpeed) {
  analogWrite(ENA, leftSpeed);
  analogWrite(ENB, rightSpeed);
}

void stopCar() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  setSpeed(0, 0);
}

void forwardCar() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  setSpeed(SPEED_FORWARD, SPEED_FORWARD);
}

void backwardCar() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  setSpeed(SPEED_FORWARD, SPEED_FORWARD);
}

void leftTurn() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  setSpeed(SPEED_TURN, SPEED_TURN);
}

void rightTurn() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  setSpeed(SPEED_TURN, SPEED_TURN);
}
