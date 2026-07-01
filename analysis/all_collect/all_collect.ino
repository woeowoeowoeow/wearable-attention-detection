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
const unsigned long sampleInterval = 250; // 4 Hz

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

        // --- Write to the already-open file ---
        bool writeOK = false;

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
            writeOK = true;
            rowCount++;
        } else {
            writeFailCount++;
        }

        // --- Also print to Serial for live monitoring ---
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