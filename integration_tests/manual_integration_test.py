import cv2
from hand_detector import HandDetector
from gesture_engine import GestureEngine
from command_handler import CommandHandler

def main():
    # 1. Modülleri Başlat
    detector = HandDetector()
    engine = GestureEngine()
    handler = CommandHandler()

    # Kamera Bağlantısı
    cap = cv2.VideoCapture(0)
    
    # --- PENCERE AYARLARI (YENİ) ---
    window_name = "Ghost Interface - Ceylin Live Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) # Pencereyi büyütülebilir yapar
    cv2.resizeWindow(window_name, 1280, 720)        # Başlangıç boyutunu ayarlar
    # ------------------------------

    print("Sistem Hazır! Çıkmak için kameraya bakarken 'q' tuşuna bas.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Kamera akışı kesildi.")
            break

        # Görüntüyü ayna moduna al (Zeynep'in tercihi)
        frame = cv2.flip(frame, 1)

        # 1. GÖZ (Zeynep): El tespiti
        frame = detector.find_hands(frame)
        landmarks = detector.get_landmark_positions(frame)

        if landmarks:
            # 2. BEYİN (Ceylin): Jest analizi
            result = engine.detect_gesture(landmarks)
            gesture = result["gesture"]
            coords = result["hand_coords"]

            # Görsel Geri Bildirim (Yeşil/Kırmızı metin)
            color = (0, 255, 0) if gesture != "unknown" else (0, 0, 255)
            cv2.putText(frame, f"JEST: {gesture.upper()}", (20, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

            # 3. ELLER (Dilara): Komutu çalıştır
            if gesture != "unknown":
                handler.execute(gesture, coords)

        # Görüntüyü Göster
        cv2.imshow(window_name, frame)

        # 'q' tuşu ile çıkış (Kamera penceresi seçiliyken basmalısın)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Kaynakları serbest bırak
    cap.release()
    cv2.destroyAllWindows()
    print("Sistem güvenli bir şekilde kapatıldı.")

if __name__ == "__main__":
    main()