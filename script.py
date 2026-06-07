import serial
import csv
import time


seri_port = 'COM3'
baud_hizi = 115200
dosya_adi = "parkinson_verileri.csv"

etiket_degeri = int(input("Şu an hangi sınıfı kaydediyorsun?\n" \
"0: Belirti yok\n1:Hafif Titreme\n 2:Şiddetli Titreme "))

if etiket_degeri == 0:
    dosya_adi = "normal_"+ dosya_adi
elif etiket_degeri == 1:
    dosya_adi = "hafif_titremeli_"+dosya_adi
elif etiket_degeri == 2:
    dosya_adi = "siddetli_titremeli_" + dosya_adi

try:
    arduino = serial.Serial(seri_port, baud_hizi, timeout=1)
    time.sleep(2)
    print(f"{seri_port} portuna bağlanıldı. Veri kaydı başlıyor. CTRL-C ile durdur.")

    with open(dosya_adi, mode='w', newline='') as dosya:
        yazici = csv.writer(dosya)
        #başlıkları ekle
        yazici.writerow(["zaman","ivme_x","ivme_y","ivme_z","etiket"])

        while True:
            if arduino.in_waiting > 0:
                satir = arduino.readline().decode("utf-8").strip()
                
                # gelen veriyi X:1.2 Y:0.5 Z:-0.1 şekline dönüştürelim
                if "X:" in satir:
                    parcalar = satir.replace("X:", "").replace("Y:", "").replace("Z:","").split()
                    if len(parcalar) == 3:
                        zaman_damgasi = time.time()
                        #etiket şimdilik 0 olsun
                        yazici.writerow([zaman_damgasi, parcalar[0], parcalar[1], parcalar[2], etiket_degeri])
                        print(f"Kaydediliyor: {parcalar}")


except KeyboardInterrupt:
    print("\n Veri kaydı durduruldu. Dosya kaydedildi.")
    arduino.close()
