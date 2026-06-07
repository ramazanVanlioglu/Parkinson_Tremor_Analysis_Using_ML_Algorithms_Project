import serial
import pandas as pd
import numpy as np
import joblib
import time

# Ayarlar
seri_port = 'COM3' 
baud_hizi = 115200
pencere_boyutu = 100 

print("Zeka (Yapay Zeka Modeli) yükleniyor...")
model = joblib.load('parkinson_modeli.pkl')

def zero_crossing_rate(arr):
    arr_centered = arr - np.mean(arr)
    return ((arr_centered[:-1] * arr_centered[1:]) < 0).sum()

try:
    arduino = serial.Serial(seri_port, baud_hizi, timeout=1)
    time.sleep(2)
    print("Bağlantı başarılı! Tahminler her 2 saniyede bir yapılacak...\n")

    buffer = [] 

    while True:
        if arduino.in_waiting > 0:
            satir = arduino.readline().decode('utf-8', errors='ignore').strip()
            
            # Veri formatını kontrol et
            if "X:" in satir:
                try:
                    parcalar = satir.replace("X:", "").replace("Y:", "").replace("Z:", "").split()
                    if len(parcalar) == 3:
                        buffer.append([float(parcalar[0]), float(parcalar[1]), float(parcalar[2])])
                        
                        # Veri toplandığını görsel olarak hissetmek için (isteğe bağlı)
                        print(f"Veri toplanıyor: {len(buffer)}/{pencere_boyutu}", end='\r')

                    if len(buffer) >= pencere_boyutu:
                        df_pencere = pd.DataFrame(buffer, columns=['x', 'y', 'z'])
                        
                        # Özellikleri hesapla (Eğitim koduyla aynı olmalı!)
                        mag = np.sqrt(df_pencere['x']**2 + df_pencere['y']**2 + df_pencere['z']**2)
                        
                        feature_dict = {
                            'mag_standart_sapma': np.std(mag),
                            'mag_varyans': np.var(mag),
                            'mag_max_min_farki': np.max(mag) - np.min(mag),
                            'mag_dalgalanma_sayisi': zero_crossing_rate(mag.values)
                        }

                        # 2. DataFrame'e çevir
                        features = pd.DataFrame([feature_dict])

                        # 3. Sıralamayı garantiye al
                        features = features[model.feature_names_in_]

                        # 4. Tahmin yap
                        tahmin = model.predict(features)[0]
                        olasilik = model.predict_proba(features).max() * 100

                        # Renkli sonuçları yazdır
                        durumlar = {0: "NORMAL", 1: "HAFİF TİTREME", 2: "ŞİDDETLİ TİTREME"}
                        # 0: Yeşil, 1: Sarı, 2: Kırmızı
                        color = "\033[92m" if tahmin == 0 else "\033[93m" if tahmin == 1 else "\033[91m"
                        
                        print(f"\n[{time.strftime('%H:%M:%S')}] TAHMİN: {color}{durumlar[tahmin]}\033[0m (Güven: %{olasilik:.1f})")
                        
                        buffer = [] # Buffer'ı sıfırla

                except Exception as e:
                    print(f"\nHata: {e}")
                    buffer = []

except KeyboardInterrupt:
    print("\nSistem kullanıcı tarafından durduruldu.")
    arduino.close()