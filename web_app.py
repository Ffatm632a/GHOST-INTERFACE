import math
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

def gen_frames():
    cap = cv2.VideoCapture(0)
    global current_gesture

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

            if gesture not in ("unknown",):
                command_handler.execute(gesture, coords)
                entry = {"time": time.strftime("%H:%M:%S"), "gesture": gesture}
                event_log.append(entry)
                if len(event_log) > 30:
                    event_log.pop(0)

            # Kare üstüne jest yaz
            color = (0, 255, 120) if gesture != "unknown" else (80, 80, 80)
            cv2.putText(frame, f"Jest: {gesture}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        except Exception as e:
            pass

        _, buf = cv2.imencode(".jpg", frame)
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
    return jsonify({
        "gesture": g,
        "log":     list(reversed(event_log))[:15],
    })

@app.route("/api/camera/status")
def camera_status():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
