import math

class GestureEngine:
    def __init__(self):
        # NFR-02: %90 doğruluk hedefi için eşik değerler 
        self.finger_tips = [8, 12, 16, 20]  # İşaret, Orta, Yüzük, Serçe uçları
        self.finger_pips = [6, 10, 14, 18]  # Parmak eklemleri

    def get_finger_status(self, landmarks):
        """
        Her parmağın açık mı kapalı mı olduğunu kontrol eder.
        Ekran koordinatlarında Y değeri yukarı gittikçe azalır.
        """
        fingers = []
        
        # Baş parmak mantığı (X koordinatına göre - Sağ/Sol el farkı olabilir)
        if landmarks[4].x < landmarks[3].x:
            fingers.append(True)
        else:
            fingers.append(False)

        # Diğer 4 parmak mantığı (Y koordinatına göre)
        for tip, pip in zip(self.finger_tips, self.finger_pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append(True) # Parmak açık
            else:
                fingers.append(False) # Parmak kapalı
                
        return fingers

    def detect_gesture(self, landmarks):
        """
        FR-04: Tanımlı jestleri belirler.
        """
        fingers = self.get_finger_status(landmarks)
        
        # UC-01: Fare Hareketi -> Tüm parmaklar açıksa (Açık Avuç) [cite: 11]
        if all(f is True for f in fingers):
            return "OPEN_PALM"
            
        # UC-07: Uygulama Aç -> Tüm parmaklar kapalıysa (Yumruk) [cite: 11]
        if all(f is False for f in fingers):
            return "FIST"

        # UC-02: Tıklama -> Sadece işaret parmağı açıksa [cite: 11]
        if fingers == [False, True, False, False, False]:
            return "POINTING_UP"

        return "UNKNOWN"
