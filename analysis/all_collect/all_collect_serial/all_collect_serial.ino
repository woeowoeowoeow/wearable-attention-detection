/*
  All Collect - Serial Only (Computer-Side CSV Logging)
  Reads EDA, MPU-6050 accelerometer, and MAX30102 PPG at 4 Hz and
  prints each sample as a CSV row over Serial. No SD card involved --
  a companion Python script on the computer captures this stream and
  writes it to a local CSV file.

  Use this if the SD card/reader is unreliable. Requires the Arduino
  to stay connected via USB for the duration of the session.
*/

#include <MAX30105.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
MAX30105 particleSensor;

unsigned long lastSampleTime = 0;
const unsigned long sampleInterval = 250; // 4 Hz

void setup() {
    Serial.begin(9600);
    delay(2000);

    Wire.begin();

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
    unsigned long currentTime = millis();

    if (currentTime - lastSampleTime >= sampleInterval) {
        lastSampleTime = currentTime;

        // --- Read EDA ---
        int rawEDA = analogRead(A0);
        float voltage = rawEDA * (5.0 / 1023.0);
        float resistance = (100000.0 * voltage) / (5.0 - voltage);
        float conductance_us = (1.0 / resistance) * 1000000.0;

        // --- Read accelerometer ---
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);

        // --- Read PPG ---
        long irValue = particleSensor.getIR();
        long redValue = particleSensor.getRed();

        // --- Print CSV row over Serial ---
        Serial.print(currentTime);
        Serial.print(",");
        Serial.print(rawEDA);
        Serial.print(",");
        Serial.print(conductance_us, 3);
        Serial.print(",");
        Serial.print(a.acceleration.x, 4);
        Serial.print(",");
        Serial.print(a.acceleration.y, 4);
        Serial.print(",");
        Serial.print(a.acceleration.z, 4);
        Serial.print(",");
        Serial.print(irValue);
        Serial.print(",");
        Serial.println(redValue);
    }
}