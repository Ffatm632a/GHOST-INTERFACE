import math

class GestureEngine:
    def __init__(self):
        self.finger_tips = [8, 12, 16, 20]
        self.finger_pips = [6, 10, 14, 18]
        self.PINCH_THRESHOLD = 0.06 # Tıklama/Zum için yakınlık eşiği

        # --- SPRINT 3: HASSASİYET FİLTRESİ (YENİ) ---
        self.history_x = []
        self.history_y = []
        self.smoothing_window = 5 # Son 5 kareyi takip eder, titremeyi yok eder.

    def smooth_coordinates(self, x, y):
        """Farenin titremesini engellemek için hareketli ortalama alır."""
        self.history_x.append(x)
        self.history_y.append(y)
        
        # Hafıza sınırını aşarsa en eski kareyi sileriz
        if len(self.history_x) > self.smoothing_window:
            self.history_x.pop(0)
            self.history_y.pop(0)
        
        # Ortalamayı hesapla (Yumuşatılmış yeni koordinat)
        avg_x = sum(self.history_x) / len(self.history_x)
        avg_y = sum(self.history_y) / len(self.history_y)
        return avg_x, avg_y

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def get_finger_status(self, landmarks):
        """Parmakların açık/kapalı durumunu belirler."""
        fingers = []
        # Baş parmak (Landmark 4 vs 3) - Yatay kontrol
        if landmarks[4].x < landmarks[3].x:
            fingers.append(True)
        else:
            fingers.append(False)
        # Diğer 4 parmak - Dikey kontrol
        for tip, pip in zip(self.finger_tips, self.finger_pips):
            fingers.append(landmarks[tip].y < landmarks[pip].y)
        return fingers

    def detect_gesture(self, landmarks):
        if not landmarks:
            # El kaybolduğunda geçmişi temizle ki yeni el gelince fare zıplamasın
            self.history_x, self.history_y = [], []
            return {"gesture": "unknown", "confidence": 0.0, "hand_coords": None}

        # --- FİLTRELEME UYGULANIYOR (YENİ) ---
        # Ham koordinatları al
        raw_x = landmarks[0].x
        raw_y = landmarks[0].y
        
        # Filtreden geçirerek yumuşatılmış koordinatları elde et
        smooth_x, smooth_y = self.smooth_coordinates(raw_x, raw_y)
        
        # Dilara'nın CommandHandler'ına gidecek 'temiz' koordinatlar
        center_coords = {"x": smooth_x, "y": smooth_y}
        # ------------------------------------

        fingers = self.get_finger_status(landmarks)
        dist_pinch = self.calculate_distance(landmarks[4], landmarks[8])
        
        gesture_name = "unknown"

        # 1. ZUM KONTROLÜ (UC-05 & UC-06)
        if dist_pinch < self.PINCH_THRESHOLD:
            gesture_name = "pinch_in"
        elif 0.06 <= dist_pinch < 0.15 and fingers[1]:
            gesture_name = "pinch_out"

        # 2. SES KONTROLÜ (UC-03 & UC-04)
        elif fingers == [True, False, False, False, False]:
            if landmarks[4].y < landmarks[5].y: # Baş parmak yukarı bakıyorsa
                gesture_name = "thumb_up"
            else:
                gesture_name = "thumb_down"

        # 3. TEMEL JESTLER (UC-01, UC-02, UC-07)
        elif all(f is True for f in fingers):
            gesture_name = "open_palm"
        elif all(f is False for f in fingers):
            gesture_name = "fist"
        elif fingers == [False, True, False, False, False]:
            gesture_name = "pointing_up"
        elif fingers == [True, True, False, False, False]: # Baş ve işaret açıksa
            gesture_name = "fist_open"

        return {
            "gesture": gesture_name,
            "confidence": 1.0,
            "hand_coords": center_coords
        }