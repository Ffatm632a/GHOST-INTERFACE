import threading
import time
import cv2
from flask import Flask, Response, jsonify, render_template
from camera_stream import CameraStream
from gesture_engine import GestureEngine
from command_handler import CommandHandler

app = Flask(__name__)

# --- Nesneler ---
gesture_engine  = GestureEngine()
command_handler = CommandHandler()

# --- Paylaşılan durum ---
current_gesture = "unknown"
gesture_lock    = threading.Lock()
event_log       = []
log_lock        = threading.Lock()

# --- Cooldown ayarları ---
COOLDOWNS = {
    "open_palm":   0,
    "swipe_right": 0.8,
    "swipe_left":  0.8,
    "thumb_up":    0.8,
    "thumb_down":  0.8,
    "pinch_in":    0.8,
    "pinch_out":   0.8,
    "fist":        0.5,
    "pointing_up": 0.5,
}
last_gesture_time = {}

def can_execute(gesture):
    cooldown = COOLDOWNS.get(gesture, 0.8)
    if cooldown == 0:
        return True
    now = time.time()
    if now - last_gesture_time.get(gesture, 0) >= cooldown:
        last_gesture_time[gesture] = now
        return True
    return False

def gen_frames():
    """Her istek için yeni CameraStream açar — kamera sızıntısı yok."""
    global current_gesture
    stream = CameraStream()

    try:
        for jpg_bytes in stream.frames():
            # jpg_bytes = MJPEG frame (--frame\r\n...); landmark bilgisi stream içinde işlendi
            # Gesture tespiti için stream.detector'dan landmark al
            if stream.detector is not None:
                landmarks = stream.detector.get_landmark_positions()
                result    = gesture_engine.detect_gesture(landmarks)
                gesture   = result["gesture"]
                coords    = result["hand_coords"]

                with gesture_lock:
                    current_gesture = gesture

                if gesture != "unknown" and can_execute(gesture):
                    command_handler.execute(gesture, coords)
                    entry = {"time": time.strftime("%H:%M:%S"), "gesture": gesture}
                    with log_lock:
                        event_log.append(entry)
                        if len(event_log) > 30:
                            event_log.pop(0)

            yield jpg_bytes

    except RuntimeError:
        # Kamera açılamadı — boş frame gönder
        import numpy as np
        blank = 10 * np.ones((480, 640, 3), dtype="uint8")
        cv2.putText(blank, "Kamera bulunamadi", (120, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 100), 2)
        _, buf = cv2.imencode(".jpg", blank)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
               + buf.tobytes() + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/status")
def api_status():
    with gesture_lock:
        g = current_gesture
    with log_lock:
        log_copy = list(reversed(event_log))[:15]
    return jsonify({"gesture": g, "log": log_copy})

@app.route("/api/camera/status")
def camera_status():
    cap = cv2.VideoCapture(0)
    ok = cap.isOpened()
    cap.release()
    return jsonify({"ok": ok})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
