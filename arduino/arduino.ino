/*
  Callback LED

  This example creates a Bluetooth® Low Energy peripheral with service that contains a
  characteristic to control an LED. The callback features of the
  library are used.

  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.

  You can use a generic Bluetooth® Low Energy central app, like LightBlue (iOS and Android) or
  nRF Connect (Android), to interact with the services and characteristics
  created in this sketch.

  This example code is in the public domain.
*/

#include <ArduinoBLE.h>

#define MOTOR_1F 10
#define MOTOR_1B 9
#define MOTOR_2F 8
#define MOTOR_2B 7
#define SPEED 180

BLEService ledService("19B10000-E8F2-537E-4F6C-D104768A1214"); // create service

// create switch characteristic and allow remote device to read and write
BLECharCharacteristic switchCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite);

void setup() { 
  pinMode(MOTOR_1F, OUTPUT);
  pinMode(MOTOR_1B, OUTPUT);
  pinMode(MOTOR_2F, OUTPUT);
  pinMode(MOTOR_2B, OUTPUT);

  Serial.begin(9600);
  // begin initialization
  if (!BLE.begin()) {
    while (1);
  }

  // set the local name peripheral advertises
  BLE.setLocalName("LEDCallback");
  // set the UUID for the service this peripheral advertises
  BLE.setAdvertisedService(ledService);

  // add the characteristic to the service
  ledService.addCharacteristic(switchCharacteristic);

  // add service
  BLE.addService(ledService);

  // assign event handlers for connected, disconnected to peripheral
  BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

  // assign event handlers for characteristic
  switchCharacteristic.setEventHandler(BLEWritten, switchCharacteristicWritten);
  // set an initial value for the characteristic
  switchCharacteristic.setValue(0);

  // start advertising
  BLE.advertise();
}

void loop() {
  // poll for Bluetooth® Low Energy events
  BLE.poll();
}

void blePeripheralConnectHandler(BLEDevice central) {
  
}

void blePeripheralDisconnectHandler(BLEDevice central) {
  
}

void switchCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic) {
  char value = switchCharacteristic.value();
  Serial.println(value);

  switch (value) {
    case 'w' :
      analogWrite(MOTOR_1B, 0);
      analogWrite(MOTOR_2B, 0);
      analogWrite(MOTOR_1F, SPEED);
      analogWrite(MOTOR_2F, SPEED);
      break;
    case 's' :
      analogWrite(MOTOR_1B, SPEED);
      analogWrite(MOTOR_2B, SPEED);
      analogWrite(MOTOR_1F, 0);
      analogWrite(MOTOR_2F, 0);
      break;
    case 'a' :
      analogWrite(MOTOR_1B, SPEED);
      analogWrite(MOTOR_2B, 0);
      analogWrite(MOTOR_1F, 0);
      analogWrite(MOTOR_2F, SPEED);
      break;
    case 'd' :
      analogWrite(MOTOR_1B, 0);
      analogWrite(MOTOR_2B, SPEED);
      analogWrite(MOTOR_1F, SPEED);
      analogWrite(MOTOR_2F, 0);
      break;
    default:
      analogWrite(MOTOR_1F, 0);
      analogWrite(MOTOR_2F, 0);
      analogWrite(MOTOR_1B, 0);
      analogWrite(MOTOR_2B, 0);
      break
  ;}
}
  
