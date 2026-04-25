import math

class GestureEngine:
    def __init__(self):
        self.finger_tips = [8, 12, 16, 20]
        self.finger_pips = [6, 10, 14, 18]
        self.PINCH_THRESHOLD = 0.06 # Tıklama/Zum için yakınlık eşiği

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
            return {"gesture": "unknown", "confidence": 0.0, "hand_coords": None}

        center_coords = {"x": landmarks[0].x, "y": landmarks[0].y}
        fingers = self.get_finger_status(landmarks)
        dist_pinch = self.calculate_distance(landmarks[4], landmarks[8])
        
        gesture_name = "unknown"

        # 1. ZUM KONTROLÜ (UC-05 & UC-06)
        if dist_pinch < self.PINCH_THRESHOLD:
            gesture_name = "pinch_in"
        elif 0.06 <= dist_pinch < 0.15 and fingers[1]: # İşaret parmağı açıksa ama mesafe orta düzeydeyse
            gesture_name = "pinch_out"

        # 2. SES KONTROLÜ (UC-03 & UC-04)
        # Sadece baş parmak açıksa (Thumb Up/Down kontrolü)
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