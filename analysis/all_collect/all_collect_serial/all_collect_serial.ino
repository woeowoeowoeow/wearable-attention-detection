/*
  All Collect - Serial Only (Computer-Side CSV Logging)
  Reads EDA, MPU-6050 accelerometer, and MAX30102 PPG at 64 Hz and
  prints each sample as a CSV row over Serial. No SD card involved --
  a companion Python script on the computer captures this stream and
  writes it to a local CSV file.

  Use this if the SD card/reader is unreliable. Requires the Arduino
  to stay connected via USB for the duration of the session.

  ================================================================
  HARDWARE WIRING REQUIRED (do not skip):
  - Connect Arduino's onboard 3.3V pin to the EDA divider circuit's
    supply rail (V_supply for the voltage divider).
  - Connect the SAME 3.3V pin to the AREF pin on the Arduino.
  - This sets the ADC's external reference to 3.3V, matching the
    formula's V_supply constant and giving full 0-1023 resolution
    over the actual 0-3.3V signal range.
  - DO NOT power the EDA circuit from 5V when using this sketch.
  ================================================================
*/

#include <MAX30105.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

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

void setup() {
    Serial.begin(9600);
    delay(2000);

    Wire.begin();

    // Set ADC reference to external 3.3V (must be wired to AREF pin)
    analogReference(EXTERNAL);

    if (!mpu.begin()) {
        Serial.println(F("MPU6050 connection failed!"));
    }

    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println(F("MAX30102 not found!"));
    } else {
        particleSensor.setup(); // default settings
    }

    // Header row -- the Python script treats the first line as CSV headers
    Serial.println(F("timestamp_ms,eda_raw,eda_conductance_us,acc_x,acc_y,acc_z,ppg_ir,ppg_red"));
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
        // V_supply = 3.3V (must match analogReference(EXTERNAL) setting and physical wiring)
        const float V_SUPPLY = 3.3;
        float voltage = rawEDA * (V_SUPPLY / 1023.0);
        // Conductance formula: G = V_out / (V_supply × R_ref - V_out × R_ref)
        // R_ref = 100kΩ, V_supply = 3.3V
        // Result in µS (microsiemens): × 1,000,000
        float conductance_us = (voltage / (V_SUPPLY * 100000.0 - voltage * 100000.0)) * 1000000.0;

        // --- Read PPG ---
        long irValue = particleSensor.getIR();
        long redValue = particleSensor.getRed();

        // --- Print CSV row over Serial (combined format, 64 Hz) ---
        // Accelerometer values use latest reading (updates every 2nd row at 32 Hz)
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
        Serial.println(redValue);
    }
}