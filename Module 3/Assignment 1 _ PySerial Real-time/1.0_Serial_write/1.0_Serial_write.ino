// ESP32 / Arduino Code
void setup() {
  Serial.begin(115200);
}

void loop() {
  // Create a simulated sine wave pattern
  // float value = 10 * sin(millis() / 1000.0) + random(-1, 2);
  float value = 10 * sin(millis() / 1000.0);
  
  // Send ONLY the value followed by a newline
  Serial.println(value);
  
  // Variable Data Rate Simulation:
  // Sometimes fast (10ms), sometimes slow (100ms)
  int randomDelay = random(10, 100); 
  delay(randomDelay);
}