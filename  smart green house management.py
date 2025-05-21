#include <Arduino_FreeRTOS.h>
#include <SPI.h>
#include <Wire.h>

#define OLED_RESET 4
#define pot_in A0
#define ldr_in A1
#define temp_in A2
#define relay_out 3
#define SPEAKER_PIN 8

const float BETA = 3950; // Beta Coefficient of the thermistor

void playBuzzerAlert() {
int notes[] = {330, 392, 659, 523, 587, 784};
for (int i = 0; i < 6; i++) {
tone(SPEAKER_PIN, notes[i]);
delay(150);
}
noTone(SPEAKER_PIN);
}

void setup() {
Serial.begin(9600);

// Pin initialization
pinMode(pot_in, INPUT);
pinMode(ldr_in, INPUT);
pinMode(temp_in, INPUT);
pinMode(relay_out, OUTPUT);
pinMode(SPEAKER_PIN, OUTPUT);

// Initial sensor readings
int moist = analogRead(pot_in);
int moist_percentage = map(moist, 0, 1024, 0, 25);
Serial.print("Starting Soil moisture: ");
Serial.print(moist_percentage);
Serial.println("% [Moisture sensor]");

int light = analogRead(ldr_in);
int light_percentage = map(light, 0, 1024, 0, 100);
Serial.print("Starting Illumination: ");
Serial.print(light_percentage);
Serial.println("% [Light sensor]");

int temp = analogRead(temp_in);
float temp_celsius = 1 / (log(1 / (1023. / temp - 1)) / BETA + 1.0 / 298.15) - 273.15;
Serial.print("Starting Temperature: ");
Serial.println(temp_celsius);

// Initial output decisions
if (light_percentage <= 50) {
digitalWrite(relay_out, HIGH);
} else {
digitalWrite(relay_out, LOW);
}

if (moist_percentage <= 10) {
playBuzzerAlert();
}

// Create RTOS tasks
xTaskCreate(Task_SoilMoisture, "Moisture Task", 128, NULL, 1, NULL);
xTaskCreate(Task_LightSensor, "Light Task", 128, NULL, 2, NULL);
xTaskCreate(Task_Temperature, "Temp Task", 128, NULL, 3, NULL);
}

void loop() {
// FreeRTOS handles everything in tasks
}

// Task 1: Soil Moisture Monitoring
void Task_SoilMoisture(void *pvParameters) {
while (1) {
int moist = analogRead(pot_in);
int moist_percentage = map(moist, 0, 1024, 0, 25);
Serial.print("Soil moisture: ");
Serial.print(moist_percentage);
Serial.println("% [Moisture sensor]");

if (moist_percentage <= 10) {
  playBuzzerAlert();
}

vTaskDelay(1000 / portTICK_PERIOD_MS);
}
}

// Task 2: Light Level Monitoring
void Task_LightSensor(void *pvParameters) {
while (1) {
int light = analogRead(ldr_in);
int light_percentage = map(light, 0, 1024, 0, 100);
Serial.print("Illumination: ");
Serial.print(light_percentage);
Serial.println("% [Light sensor]");

if (light_percentage <= 50) {
  digitalWrite(relay_out, HIGH);
} else {
  digitalWrite(relay_out, LOW);
}

vTaskDelay(1100 / portTICK_PERIOD_MS);
}
}

// Task 3: Temperature Monitoring
void Task_Temperature(void *pvParameters) {
while (1) {
int temp = analogRead(temp_in);
float temp_celsius = 1 / (log(1 / (1023.0 / temp - 1)) / BETA + 1.0 / 298.15) - 273.15;
Serial.print("Temperature: ");
Serial.print(temp_celsius);
Serial.println(" C [Temperature sensor]");

vTaskDelay(1100 / portTICK_PERIOD_MS);
}
}