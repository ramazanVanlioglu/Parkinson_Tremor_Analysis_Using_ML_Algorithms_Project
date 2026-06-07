#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

#define I2C_SDA 8 // I2C pin tanımlamaları
#define I2C_SCL 9

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire); // BNO055 sensör

void setup(void) {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.println("Parkinson Veri Toplama Sistemi Baslatiliyor.");

  if (!bno.begin()) {
    Serial.print("BNO055 yanit vermedi.");
    while (1);
  }
  delay(1000);
  bno.setExtCrystalUse(true);
}

void loop(void) {
  // Lineer İvme verisi al (Bu veride sadece titreme ve hareket vardır)
  imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  // Parkinson titremelerini analiz etmek için X, Y ve Z eksenlerini yazdıralım
  Serial.print("X:"); Serial.print(accel.x()); Serial.print(" ");
  Serial.print("Y:"); Serial.print(accel.y()); Serial.print(" ");
  Serial.print("Z:"); Serial.println(accel.z());

  delay(20); // 50Hz örnekleme hızı, tıbbi veriler için yeterlidir.
}