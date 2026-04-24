import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os

MODEL_PATH = "hand_landmarker.task"

# El bağlantıları - hangi noktalar birbirine çizgi ile bağlanacak
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),        # baş parmak
    (0,5),(5,6),(6,7),(7,8),        # işaret parmağı
    (0,9),(9,10),(10,11),(11,12),   # orta parmak
    (0,13),(13,14),(14,15),(15,16), # yüzük parmağı
    (0,17),(17,18),(18,19),(19,20), # serçe
    (5,9),(9,13),(13,17)            # avuç içi
]

class HandDetector:

    def __init__(self):
        base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.last_landmarks = []

    def find_hands(self, frame, draw=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect(mp_image)

        self.last_landmarks = []

        if result.hand_landmarks:
            h, w, _ = frame.shape
            hand = result.hand_landmarks[0]

            for idx, lm in enumerate(hand):
                cx = int(lm.x * w)
                cy = int(lm.y * h)
                self.last_landmarks.append((idx, cx, cy))

            if draw:
                # Bağlantı çizgilerini çiz
                for start_idx, end_idx in HAND_CONNECTIONS:
                    start = self.last_landmarks[start_idx]
                    end = self.last_landmarks[end_idx]
                    cv2.line(frame, (start[1], start[2]), (end[1], end[2]),
                            (0, 255, 0), 2)

                # Landmark noktalarını çiz
                for (idx, cx, cy) in self.last_landmarks:
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 255), -1)

        return frame

    def get_landmark_positions(self, frame):
        return self.last_landmarks


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    print("El dedektörü çalışıyor. Çıkmak için 'q' bas.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.find_hands(frame)
        landmarks = detector.get_landmark_positions(frame)

        if landmarks:
            tip = landmarks[8]
            cv2.putText(frame, f"El tespit edildi! Nokta sayisi: {len(landmarks)}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Isaret parmagi: ({tip[1]}, {tip[2]})",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "El bulunamadi - elini goster",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Hand Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()