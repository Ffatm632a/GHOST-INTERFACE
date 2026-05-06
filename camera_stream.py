import time

import cv2

from hand_detector import HandDetector


class CameraStream:
    """Web arayuzu icin kamera goruntusunu landmark cizimiyle uretir."""

    def __init__(self, camera_index=0, width=960, height=540):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.detector = None
        self.frame_count = 0
        self.last_landmark_count = 0
        self.started_at = None

    def frames(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            raise RuntimeError("Webcam acilamadi.")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.detector = HandDetector()
        self.started_at = time.time()

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                frame = cv2.flip(frame, 1)
                frame = self.detector.find_hands(frame, draw=True)
                landmarks = self.detector.get_landmark_positions(frame)

                self.frame_count += 1
                self.last_landmark_count = len(landmarks)
                self._draw_status(frame, self.last_landmark_count)

                encoded, buffer = cv2.imencode(".jpg", frame)
                if not encoded:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + buffer.tobytes()
                    + b"\r\n"
                )
        finally:
            cap.release()
            if self.detector is not None:
                self.detector.close()
                self.detector = None
            self.started_at = None

    def status(self):
        elapsed = 0 if self.started_at is None else time.time() - self.started_at
        fps = 0 if elapsed == 0 else round(self.frame_count / elapsed, 2)
        return {
            "camera_index": self.camera_index,
            "frame_count": self.frame_count,
            "last_landmark_count": self.last_landmark_count,
            "fps": fps,
            "running": self.started_at is not None,
        }

    @staticmethod
    def _draw_status(frame, landmark_count):
        if landmark_count:
            text = f"El tespit edildi: {landmark_count} landmark"
            color = (0, 255, 0)
        else:
            text = "El bulunamadi"
            color = (0, 0, 255)

        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
