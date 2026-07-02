/*
  Connection Test - All Sensors
  Checks: MPU-6050 (I2C), MAX30102 (I2C), EDA voltage divider (analog),
  MicroSD module (SPI)
  
  Run this BEFORE every self-calibration session. Fix anything that
  shows FAIL before starting -- don't proceed with a partial pass.
*/

#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// ---- Pin config -- adjust to match your wiring ----
const int EDA_PIN = A0;
const int SD_CS_PIN = 10;

// ---- I2C addresses ----
const byte MPU6050_ADDR = 0x68;
const byte MAX30102_ADDR = 0x57;

bool mpuOK = false;
bool maxOK = false;
bool sdOK = false;
bool edaOK = false;

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }
  delay(500);

  Serial.println("=========================================");
  Serial.println("   SENSOR CONNECTION TEST");
  Serial.println("=========================================");

  Wire.begin();

  testI2CDevice(MPU6050_ADDR, "MPU-6050", mpuOK);
  testI2CDevice(MAX30102_ADDR, "MAX30102", maxOK);
  testSD();
  testEDA();

  Serial.println("-----------------------------------------");
  Serial.println("SUMMARY:");
  printResult("MPU-6050 (accel/gyro)", mpuOK);
  printResult("MAX30102 (PPG)", maxOK);
  printResult("MicroSD module", sdOK);
  printResult("EDA circuit (range check)", edaOK);
  Serial.println("-----------------------------------------");

  if (mpuOK && maxOK && sdOK && edaOK) {
    Serial.println("ALL SYSTEMS GO. Safe to start session.");
  } else {
    Serial.println("DO NOT START SESSION. Fix failures above first.");
  }
  Serial.println("=========================================");
}

void loop() {
  // After the initial test, continuously stream live values so you
  // can visually confirm signals respond to movement/touch before
  // committing to a full session.
  printLiveReadings();
  delay(500);
}

// ---------------- Test functions ----------------

void testI2CDevice(byte addr, const char* name, bool &okFlag) {
  Serial.print("Testing ");
  Serial.print(name);
  Serial.print(" at address 0x");
  Serial.print(addr, HEX);
  Serial.print(" ... ");

  Wire.beginTransmission(addr);
  byte error = Wire.endTransmission();

  if (error == 0) {
    Serial.println("FOUND");
    okFlag = true;
  } else {
    Serial.println("NOT FOUND -- check wiring/power");
    okFlag = false;
  }
}

void testSD() {
  Serial.print("Testing MicroSD module ... ");
  if (SD.begin(SD_CS_PIN)) {
    Serial.println("OK");
    // Quick write/read round-trip to confirm it actually works,
    // not just initializes
    File testFile = SD.open("test.txt", FILE_WRITE);
    if (testFile) {
      testFile.println("connection_test_ok");
      testFile.close();
      sdOK = true;
    } else {
      Serial.println("  (init OK but file write failed)");
      sdOK = false;
    }
  } else {
    Serial.println("FAILED -- check CS pin, wiring, card seated");
    sdOK = false;
  }
}

void testEDA() {
  Serial.print("Testing EDA circuit ... ");
  int raw = analogRead(EDA_PIN);
  Serial.print("raw reading = ");
  Serial.print(raw);

  // Sanity range check -- adjust bounds once you know your circuit's
  // expected resting range. 0 or 1023 (rail-to-rail) usually means
  // a wiring fault (open or short circuit), not real skin conductance.
  if (raw > 5 && raw < 1018) {
    Serial.println(" -- in plausible range");
    edaOK = true;
  } else {
    Serial.println(" -- at rail, check electrode contact/wiring");
    edaOK = false;
  }
}

void printResult(const char* name, bool ok) {
  Serial.print(name);
  Serial.print(": ");
  Serial.println(ok ? "PASS" : "FAIL");
}

// ---------------- Live readings (loop) ----------------

void printLiveReadings() {
  int edaRaw = analogRead(EDA_PIN);

  Serial.print("EDA raw: ");
  Serial.print(edaRaw);

  // Light-touch read of accel registers to confirm live motion response
  // without pulling in a full MPU-6050 library dependency
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B); // ACCEL_XOUT_H register
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, (uint8_t)6, true);

  if (Wire.available() == 6) {
    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();
    Serial.print(" | Accel X:");
    Serial.print(ax);
    Serial.print(" Y:");
    Serial.print(ay);
    Serial.print(" Z:");
    Serial.print(az);
  } else {
    Serial.print(" | Accel: no data");
  }

  Serial.println();
}