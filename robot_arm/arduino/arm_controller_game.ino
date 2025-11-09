/*
  JADE Robotic Arm Controller - Game Controller Compatible
  Supports both:
  1. Keyboard commands (Q/A W/S E/D R/F T/G)
  2. Serial commands (servo_id:angle; format)
  
  Compatible with arm_control_game.py
*/

#include <Servo.h>

Servo servos[5];
int servoPins[5] = {7, 3, 4, 5, 6};  // Adjust pins to match your hardware
int servoAngles[5]; // Current servo angles

String inputBuffer = "";
bool commandReady = false;

void setup() {
  Serial.begin(9600);
  
  // Initialize pins LOW to reduce twitch
  for (int i = 0; i < 5; i++) {
    pinMode(servoPins[i], OUTPUT);
    digitalWrite(servoPins[i], LOW);
    servos[i].attach(servoPins[i]);
    servoAngles[i] = 90; // Start at middle position
    servos[i].write(servoAngles[i]);
  }

  Serial.println("JADE Arm Controller Ready");
  Serial.println("Commands: servo_id:angle; (e.g., '0:90;')");
  Serial.println("Or keyboard: Q/A W/S E/D R/F T/G");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    
    // Check if it's a keyboard command (single character)
    if (c >= 'a' && c <= 'z') {
      handleKeyboardCommand(c);
    }
    // Otherwise, build command string
    else if (c == ';') {
      commandReady = true;
    }
    else if ((c >= '0' && c <= '9') || c == ':') {
      inputBuffer += c;
    }
    
    // Process complete command
    if (commandReady) {
      processSerialCommand(inputBuffer);
      inputBuffer = "";
      commandReady = false;
    }
  }
}

void handleKeyboardCommand(char c) {
  // Keyboard control - same as original game controller
  if      (c == 'q') setServoAngle(0, min(servoAngles[0]+10, 180));
  else if (c == 'a') setServoAngle(0, max(servoAngles[0]-10, 0));
  else if (c == 'w') setServoAngle(1, min(servoAngles[1]+10, 180));
  else if (c == 's') setServoAngle(1, max(servoAngles[1]-10, 0));
  else if (c == 'e') setServoAngle(2, min(servoAngles[2]+10, 180));
  else if (c == 'd') setServoAngle(2, max(servoAngles[2]-10, 0));
  else if (c == 'r') setServoAngle(3, min(servoAngles[3]+10, 180));
  else if (c == 'f') setServoAngle(3, max(servoAngles[3]-10, 0));
  else if (c == 't') setServoAngle(4, min(servoAngles[4]+10, 180));
  else if (c == 'g') setServoAngle(4, max(servoAngles[4]-10, 0));
}

void processSerialCommand(String cmd) {
  // Parse command format: "servo_id:angle"
  // Example: "0:90" sets servo 0 to 90 degrees
  
  int colonIndex = cmd.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR: Invalid command format. Use 'id:angle;'");
    return;
  }
  
  String servoIdStr = cmd.substring(0, colonIndex);
  String angleStr = cmd.substring(colonIndex + 1);
  
  int servoId = servoIdStr.toInt();
  int angle = angleStr.toInt();
  
  // Validate
  if (servoId < 0 || servoId >= 5) {
    Serial.print("ERROR: Invalid servo ID: ");
    Serial.println(servoId);
    return;
  }
  
  if (angle < 0 || angle > 180) {
    Serial.print("ERROR: Invalid angle: ");
    Serial.println(angle);
    return;
  }
  
  // Set servo position
  setServoAngle(servoId, angle);
  
  // Send confirmation
  Serial.print("OK: Servo ");
  Serial.print(servoId);
  Serial.print(" -> ");
  Serial.println(angle);
}

void setServoAngle(int servoId, int angle) {
  // Constrain angle to valid range
  angle = constrain(angle, 0, 180);
  
  // Update and move servo
  servoAngles[servoId] = angle;
  servos[servoId].write(angle);
}
