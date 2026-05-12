import threading
import time
import cv2
from flask import Flask, Response, jsonify, render_template
from hand_detector import HandDetector
from gesture_engine import GestureEngine
from command_handler import CommandHandler

app = Flask(__name__)

# --- Nesneler ---
hand_detector   = HandDetector()
gesture_engine  = GestureEngine()
command_handler = CommandHandler()

# --- Paylaşılan durum ---
current_gesture = "unknown"
gesture_lock    = threading.Lock()
event_log       = []
log_lock        = threading.Lock()  # event_log için ayrı lock

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
    last = last_gesture_time.get(gesture, 0)
    if now - last >= cooldown:
        last_gesture_time[gesture] = now
        return True
    return False

def gen_frames():
    cap = cv2.VideoCapture(0)
    global current_gesture

    if not cap.isOpened():
        hand_detector.close()
        return

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)

            try:
                frame     = hand_detector.find_hands(frame, draw=True)
                landmarks = hand_detector.get_landmark_positions()
                result    = gesture_engine.detect_gesture(landmarks)
                gesture   = result["gesture"]
                coords    = result["hand_coords"]

                with gesture_lock:
                    current_gesture = gesture

                if gesture not in ("unknown",) and can_execute(gesture):
                    command_handler.execute(gesture, coords)
                    entry = {"time": time.strftime("%H:%M:%S"), "gesture": gesture}
                    with log_lock:
                        event_log.append(entry)
                        if len(event_log) > 30:
                            event_log.pop(0)

                color = (0, 255, 120) if gesture != "unknown" else (80, 80, 80)
                cv2.putText(frame, f"Jest: {gesture}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

            except Exception:
                pass

            _, buf = cv2.imencode(".jpg", frame)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                   + buf.tobytes() + b"\r\n")
    finally:
        cap.release()


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
