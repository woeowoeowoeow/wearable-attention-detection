void setup() {
    Serial.begin(9600);
}

void loop() {
    int raw = analogRead(A0);
    float voltage = raw * (5.0 / 1023.0);
    float resistance = (100000.0 * voltage) / (5.0 - voltage);
    float conductance_us = (1.0 / resistance) * 1000000.0;
    
    Serial.println(conductance_us, 3);
    
    delay(250);
}