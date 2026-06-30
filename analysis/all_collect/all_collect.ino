#include <MAX30105.h>
#include <heartRate.h>
#include <spo2_algorithm.h>

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

const int chipSelect = 10;
File dataFile;

Adafruit_MPU6050 mpu;
MAX30105 particleSensor;

unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 250; // 4 Hz

void setup() {
    Serial.begin(9600);
    delay(2000);
    Serial.println("Starting setup...");

    Wire.begin();

    // Initialize SD card
    if (!SD.begin(chipSelect)) {
        Serial.println("SD initialization failed!");
        return;
    }
    Serial.println("SD initialized.");

    // Initialize MPU-6050
    if (!mpu.begin()) {
        Serial.println("MPU6050 connection failed!");
    } else {
        Serial.println("MPU6050 connected.");
    }

    // Initialize MAX30102
    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println("MAX30102 not found!");
    } else {
        Serial.println("MAX30102 connected.");
        particleSensor.setup(); // default settings
    }

    // Write CSV header once at the start
    dataFile = SD.open("session_log.csv", FILE_WRITE);
    if (dataFile) {
        dataFile.println("timestamp_ms,eda_raw,eda_conductance_us,"
                          "acc_x,acc_y,acc_z,ppg_ir,ppg_red");
        dataFile.close();
    }

    Serial.println("Setup complete. Starting loop...");
}

void loop() {
    unsigned long currentTime = millis();

    if (currentTime - lastSampleTime >= sampleInterval) {
        lastSampleTime = currentTime;

        // --- Read EDA ---
        int rawEDA = analogRead(A0);
        float voltage = rawEDA * (5.0 / 1023.0);
        float resistance = (100000.0 * voltage) / (5.0 - voltage);
        float conductance_us = (1.0 / resistance) * 1000000.0;

        // --- Read accelerometer (Adafruit API) ---
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        float ax = a.acceleration.x;
        float ay = a.acceleration.y;
        float az = a.acceleration.z;

        // --- Read PPG ---
        long irValue = particleSensor.getIR();
        long redValue = particleSensor.getRed();

        // --- Write everything to one CSV row ---
        dataFile = SD.open("session_log.csv", FILE_WRITE);
        if (dataFile) {
            dataFile.print(currentTime);
            dataFile.print(",");
            dataFile.print(rawEDA);
            dataFile.print(",");
            dataFile.print(conductance_us, 3);
            dataFile.print(",");
            dataFile.print(ax, 4);
            dataFile.print(",");
            dataFile.print(ay, 4);
            dataFile.print(",");
            dataFile.print(az, 4);
            dataFile.print(",");
            dataFile.print(irValue);
            dataFile.print(",");
            dataFile.println(redValue);
            dataFile.close();
        }

        // Also print to Serial for live monitoring
        Serial.print(currentTime);
        Serial.print(",");
        Serial.print(conductance_us, 3);
        Serial.print(",");
        Serial.print(ax, 4);
        Serial.print(",");
        Serial.print(ay, 4);
        Serial.print(",");
        Serial.print(az, 4);
        Serial.print(",");
        Serial.print(irValue);
        Serial.print(",");
        Serial.println(redValue);
    }
}