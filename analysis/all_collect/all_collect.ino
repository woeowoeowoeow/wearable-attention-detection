#include <MAX30105.h>

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
const unsigned long sampleInterval = 15625; // 64 Hz (1000000 µs / 64 = 15625 µs)

unsigned long lastAccTime = 0;
const unsigned long accInterval = 31250; // 32 Hz (1000000 µs / 32 = 31250 µs)

// Store latest accelerometer values for use on non-acc sample cycles
float lastAccX = 0;
float lastAccY = 0;
float lastAccZ = 0;

unsigned long lastFlush = 0;
const unsigned long flushInterval = 1000; // flush to SD once per second

unsigned long rowCount = 0;
unsigned long writeFailCount = 0;

void setup() {
    Serial.begin(9600);
    delay(2000);
    Serial.println(F("Starting setup..."));

    Wire.begin();

    // Initialize SD card
    if (!SD.begin(chipSelect)) {
        Serial.println(F("SD initialization failed!"));
        return;
    }
    Serial.println(F("SD initialized."));

    // Initialize MPU-6050
    if (!mpu.begin()) {
        Serial.println(F("MPU6050 connection failed!"));
    } else {
        Serial.println(F("MPU6050 connected."));
    }

    // Initialize MAX30102
    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println(F("MAX30102 not found!"));
    } else {
        Serial.println(F("MAX30102 connected."));
        particleSensor.setup(); // default settings
    }

    // Right before opening the file in setup():
    if (SD.exists("session_log.csv")) {
        SD.remove("session_log.csv");
        Serial.println(F("Removed old session_log.csv"));
    }

    // Open the file ONCE and keep it open for the whole session
    dataFile = SD.open("session_log.csv", FILE_WRITE);
    if (dataFile) {
        dataFile.println(F("timestamp_ms,eda_raw,eda_conductance_us,"
                            "acc_x,acc_y,acc_z,ppg_ir,ppg_red"));
        dataFile.flush();
        Serial.println(F("CSV header written to SD."));
    } else {
        Serial.println(F("WARNING: failed to open session_log.csv!"));
    }

    lastFlush = millis();
    Serial.println(F("Setup complete. Starting loop..."));
}

void loop() {
    unsigned long currentTime = micros();

    // --- Independent 32 Hz accelerometer sampling ---
    if (currentTime - lastAccTime >= accInterval) {
        lastAccTime = currentTime;
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        lastAccX = a.acceleration.x;
        lastAccY = a.acceleration.y;
        lastAccZ = a.acceleration.z;
    }

    // --- 64 Hz EDA + PPG sampling with combined CSV output ---
    if (currentTime - lastSampleTime >= sampleInterval) {
        lastSampleTime = currentTime;

        // --- Read EDA ---
        int rawEDA = analogRead(A0);
        float voltage = rawEDA * (3.3 / 1023.0);
        // Conductance formula: G = V_out / (V_supply × R_ref - V_out × R_ref)
        // R_ref = 100kΩ, V_supply = 3.3V
        float conductance_us = (voltage / (3.3 * 100000.0 - voltage * 100000.0)) * 1000000.0;

        // --- Read PPG ---
        long irValue = particleSensor.getIR();
        long redValue = particleSensor.getRed();

        // --- Write to the already-open file (combined format, 64 Hz) ---
        // Accelerometer values use latest reading (updates every 2nd row at 32 Hz)
        bool writeOK = false;

        if (dataFile) {
            dataFile.print(currentTime);
            dataFile.print(",");
            dataFile.print(rawEDA);
            dataFile.print(",");
            dataFile.print(conductance_us, 3);
            dataFile.print(",");
            dataFile.print(lastAccX, 4);
            dataFile.print(",");
            dataFile.print(lastAccY, 4);
            dataFile.print(",");
            dataFile.print(lastAccZ, 4);
            dataFile.print(",");
            dataFile.print(irValue);
            dataFile.print(",");
            dataFile.println(redValue);
            writeOK = true;
            rowCount++;
        } else {
            writeFailCount++;
        }

        // --- Also print to Serial for live monitoring ---
        Serial.print(currentTime);
        Serial.print(",");
        Serial.print(rawEDA);
        Serial.print(",");
        Serial.print(conductance_us, 3);
        Serial.print(",");
        Serial.print(lastAccX, 4);
        Serial.print(",");
        Serial.print(lastAccY, 4);
        Serial.print(",");
        Serial.print(lastAccZ, 4);
        Serial.print(",");
        Serial.print(irValue);
        Serial.print(",");
        Serial.print(redValue);

        if (writeOK) {
            Serial.print(F(" | SD OK (row "));
            Serial.print(rowCount);
            Serial.println(")");
        } else {
            Serial.print(F(" | SD WRITE FAILED (fail count: "));
            Serial.print(writeFailCount);
            Serial.println(")");
        }
    }

    // --- Periodically flush so data is physically committed to the card ---
    if (millis() - lastFlush >= flushInterval) {
        lastFlush = millis();
        if (dataFile) {
            dataFile.flush();
        }
    }
}