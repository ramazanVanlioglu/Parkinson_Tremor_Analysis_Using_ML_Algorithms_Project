import requests
import joblib
import serial
import pandas as pd
import numpy as np
import time

# AYARLAR
BLYNK_AUTH = 'ONGLqrqbiGih0rMWin5pybhnJpWTnf66'
seri_port = 'COM3' 
model = joblib.load('parkinson_modeli.pkl')
arduino = serial.Serial(seri_port, 115200, timeout=1)

def blynk_gonder(pin, deger):
    try:
        url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}&{pin}={deger}"
        requests.get(url, timeout=2)
    except:
        print("Blynk'e gönderken hata oluştu.")

buffer = []
print("Sistem HTTP Modu ile Başlatılıyor.")

while True:
    if arduino.in_waiting > 0:
        satir = arduino.readline().decode('utf-8', errors='ignore').strip()
        
        if "X:" in satir:
            try:
                parcalar = satir.replace("X:", "").replace("Y:", "").replace("Z:", "").split()
                if len(parcalar) == 3:
                    x, y, z = float(parcalar[0]), float(parcalar[1]), float(parcalar[2])
                    mag = np.sqrt(x**2 + y**2 + z**2)
                    buffer.append([x, y, z, mag])

                if len(buffer) >= 100:
                    df = pd.DataFrame(buffer, columns=['x', 'y', 'z', 'mag'])
                    
                    # özellik hesabı
                    features = pd.DataFrame([{
                        'mag_standart_sapma': np.std(df['mag']),
                        'mag_varyans': np.var(df['mag']),
                        'mag_max_min_farki': np.max(df['mag']) - np.min(df['mag']),
                        'mag_dalgalanma_sayisi': (((df['mag'] - df['mag'].mean())[:-1].values * (df['mag'] - df['mag'].mean())[1:].values) < 0).sum()
                    }])

                    tahmin = model.predict(features[model.feature_names_in_])[0]
                    olasilik = model.predict_proba(features[model.feature_names_in_]).max() * 100
                    
                    durumlar = {0: "NORMAL", 1: "HAFIF TITREME", 2: "SIDDETLI TITREME"}
                    sonuc = durumlar[tahmin]

                    # Blynk'e http ile gönder
                    blynk_gonder("V0", "Şu anki tremor seviyesi: "+sonuc)
                    blynk_gonder("V1", "Tahminin olasılık değeri: "+str(int(olasilik)))
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Tahmin Mobile İletildi: {sonuc}")
                    buffer = []
            except Exception as e:
                print(f"Hata: {e}")