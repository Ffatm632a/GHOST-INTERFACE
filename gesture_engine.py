import math

class GestureEngine:
    def __init__(self):
        self.finger_tips = [8, 12, 16, 20]
        self.finger_pips = [6, 10, 14, 18]
        self.PINCH_THRESHOLD = 0.06
        self.history_x = []
        self.history_y = []
        self.smoothing_window = 5

        # Swipe tespiti için
        self.swipe_history = []
        self.swipe_window = 8       # Son 8 kare
        self.swipe_threshold = 0.15 # En az %15 ekran genişliği hareket

    def smooth_coordinates(self, x, y):
        self.history_x.append(x)
        self.history_y.append(y)
        if len(self.history_x) > self.smoothing_window:
            self.history_x.pop(0)
            self.history_y.pop(0)
        return sum(self.history_x)/len(self.history_x), sum(self.history_y)/len(self.history_y)

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def get_finger_status(self, landmarks):
        fingers = []
        if landmarks[4].x < landmarks[3].x:
            fingers.append(True)
        else:
            fingers.append(False)
        for tip, pip in zip(self.finger_tips, self.finger_pips):
            fingers.append(landmarks[tip].y < landmarks[pip].y)
        return fingers

    def detect_swipe(self, x):
        """Sağa/sola kaydırma tespiti."""
        self.swipe_history.append(x)
        if len(self.swipe_history) > self.swipe_window:
            self.swipe_history.pop(0)

        if len(self.swipe_history) >= self.swipe_window:
            delta = self.swipe_history[-1] - self.swipe_history[0]
            if delta > self.swipe_threshold:
                self.swipe_history = []
                return "swipe_right"
            elif delta < -self.swipe_threshold:
                self.swipe_history = []
                return "swipe_left"
        return None

    def detect_gesture(self, landmarks):
        if not landmarks:
            self.history_x, self.history_y = [], []
            self.swipe_history = []
            return {"gesture": "unknown", "confidence": 0.0, "hand_coords": None}

        raw_x = landmarks[0].x
        raw_y = landmarks[0].y
        smooth_x, smooth_y = self.smooth_coordinates(raw_x, raw_y)
        center_coords = {"x": smooth_x, "y": smooth_y}

        fingers = self.get_finger_status(landmarks)
        dist_pinch = self.calculate_distance(landmarks[4], landmarks[8])

        gesture_name = "unknown"

        # 1. ZUM
        if dist_pinch < self.PINCH_THRESHOLD:
            gesture_name = "pinch_in"
        elif 0.06 <= dist_pinch < 0.15 and fingers[1]:
            gesture_name = "pinch_out"

        # 2. SES
        elif fingers == [True, False, False, False, False]:
            if landmarks[4].y < landmarks[5].y:
                gesture_name = "thumb_up"
            else:
                gesture_name = "thumb_down"

        # 3. SWIPE (açık el ile sağa/sola)
        elif all(f is True for f in fingers):
            swipe = self.detect_swipe(landmarks[0].x)
            if swipe:
                gesture_name = swipe
            else:
                gesture_name = "open_palm"

        # 4. DİĞER JESTLER
        elif all(f is False for f in fingers):
            gesture_name = "fist"
        elif fingers == [False, True, False, False, False]:
            gesture_name = "pointing_up"

        return {
            "gesture": gesture_name,
            "confidence": 1.0,
            "hand_coords": center_coords
        }
