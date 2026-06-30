#include <SPI.h>
#include <SD.h>

const int chipSelect = 10;
File dataFile;

void setup() {
    Serial.begin(9600);
    if (!SD.begin(chipSelect)) {
        Serial.println("SD initialization failed!");
        return;
    }
    Serial.println("SD initialized.");
}

void loop() {
    int raw = analogRead(A0);
    float voltage = raw * (5.0 / 1023.0);
    float resistance = (100000.0 * voltage) / (5.0 - voltage);
    float conductance_us = (1.0 / resistance) * 1000000.0;
    
    unsigned long timestamp = millis();
    
    dataFile = SD.open("eda_log.csv", FILE_WRITE);
    if (dataFile) {
        dataFile.print(timestamp);
        dataFile.print(",");
        dataFile.println(conductance_us, 3);
        dataFile.close();
    } else {
        Serial.println("Error opening file");
    }
    
    Serial.println(conductance_us, 3);
    
    delay(250);
}