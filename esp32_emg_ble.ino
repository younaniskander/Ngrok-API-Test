#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Define the exact UUIDs required by the Web Dashboard JavaScript
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Define the ADC pins for the 4 EMG sensors
// (Compatible with standard ESP32 ADC1 pins)
const int EMG_PIN_1 = 32; // Recto Femoral (RF)
const int EMG_PIN_2 = 33; // Biceps Femoral (BF)
const int EMG_PIN_3 = 34; // Vasto Medial (VM)
const int EMG_PIN_4 = 35; // Semitendinoso (ST)

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      Serial.println("Device connected! Streaming starting...");
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      Serial.println("Device disconnected!");
    }
};

void setup() {
  Serial.begin(115200);
  
  // Initialize ADC attenuation (allows reading up to ~3.3V)
  analogSetPinAttenuation(EMG_PIN_1, ADC_11db);
  analogSetPinAttenuation(EMG_PIN_2, ADC_11db);
  analogSetPinAttenuation(EMG_PIN_3, ADC_11db);
  analogSetPinAttenuation(EMG_PIN_4, ADC_11db);

  // Initialize BLE. The name "ESP32_Exoskeleton_EMG" allows the 
  // web browser's bluetooth filter (namePrefix: "ESP32") to find it.
  BLEDevice::init("ESP32_Exoskeleton_EMG");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic to send data
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                    );

  // Add a descriptor (required for notifications)
  pCharacteristic->addDescriptor(new BLE2902());

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  Serial.println("BLE Advertising Started. Waiting for web dashboard to connect...");
}

void loop() {
    if (deviceConnected) {
        // Read raw ADC values (12-bit resolution: 0-4095)
        int raw1 = analogRead(EMG_PIN_1);
        int raw2 = analogRead(EMG_PIN_2);
        int raw3 = analogRead(EMG_PIN_3);
        int raw4 = analogRead(EMG_PIN_4);

        // Convert raw values to simulated voltage (~0.0 to ~3.3V)
        // Note: You may need to apply calibration/mapping depending on your actual EMG sensors
        float v1 = (raw1 / 4095.0) * 3.3;
        float v2 = (raw2 / 4095.0) * 3.3;
        float v3 = (raw3 / 4095.0) * 3.3;
        float v4 = (raw4 / 4095.0) * 3.3;

        // Format as a comma-separated string matching the UI's expectations:
        // "ch1,ch2,ch3,ch4"
        String dataString = String(v1, 3) + "," + 
                            String(v2, 3) + "," + 
                            String(v3, 3) + "," + 
                            String(v4, 3);
                            
        // Send the string as a BLE notification
        pCharacteristic->setValue(dataString.c_str());
        pCharacteristic->notify();
        
        // Brief delay. 10ms = ~100Hz sampling rate.
        delay(10); 
    }

    // Handle sudden disconnections: restart advertising
    if (!deviceConnected && oldDeviceConnected) {
        delay(500); // give the bluetooth stack a moment
        pServer->startAdvertising(); 
        Serial.println("Restarted Advertising");
        oldDeviceConnected = deviceConnected;
    }
    
    // Handle new connection state updates
    if (deviceConnected && !oldDeviceConnected) {
        oldDeviceConnected = deviceConnected;
    }
}
