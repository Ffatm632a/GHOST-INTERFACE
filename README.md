# GHOST-INTERFACE

This project is an interface project that aims to control computer systems with hand gestures, without physical contact, using artificial intelligence and image processing techniques.

## Project Purpose

Using the MediaPipe and OpenCV libraries, the project detects hand landmark points and generates meaningful "gestures" from the relative positions of these points to provide mouse control, volume adjustment, or application management.

---

## Team and Task Distribution

* **Zeynep Karatas (Member 1):** Camera stream, hand detection, and Web API integration. (`hand_detector.py`, `camera_stream.py`)
* **Ceylin Guzelgorur (Member 2):** Gesture recognition engine, mathematical analysis, and sensitivity filter. (`gesture_engine.py`)
* **Dilara Bilisik (Member 3):** System integration, command management, and testing processes. (`command_handler.py`, `config.json`)
* **Elif Rumeysa Demir (Member 4):** Web interface and user dashboard development. (`web_app.py`)

---

## Technologies Used

* **Python 3.10+**
* **OpenCV & MediaPipe:** Image processing and hand landmark analysis.
* **Flask:** Web-based control panel and live streaming.
* **PyAutoGUI & Keyboard:** System-level command triggers.

---

## System Workflow

The system works in a modular structure and converts hand data into commands:

### Supported Gestures and Command Table

| Gesture | Command | Description |
|------|-------|----------|
| `open_palm` | `mouse_move` | Moves the mouse cursor to the hand position |
| `fist` | `left_click` | Performs a left mouse click |
| `thumb_up` | `volume_up` | Increases the system volume |
| `thumb_down` | `volume_down` | Decreases the system volume |
| `pinch_out` | `zoom_in` | Zooms in on the screen (Ctrl+) |
| `pinch_in` | `zoom_out` | Zooms out on the screen (Ctrl-) |
| `fist_open` | `open_app` | Opens the defined application (Notepad, etc.) |

---

## Technical Details (Module 3)

### config.json Structure

To add new gestures, no code change is required; only the configuration file is edited:

```json
{
  "gestures": { "gesture_name": "command_name" },
  "app_to_open": "notepad",
  "volume_step": 5,
  "zoom_step": 0.1
}
```

### Platform Support

Our project is optimized to trigger local commands on different operating systems:

| Platform | Volume Control Mechanism | Application Launch |
|----------|-------------------------|-------------------|
| **Windows 10/11** | `keyboard.send("volume up/down")` | `subprocess.Popen(shell=True)` |
| **Linux (Ubuntu)** | `amixer -D pulse sset Master` | `subprocess.Popen([app])` |
| **macOS** | `osascript -e "set volume..."` | `subprocess.Popen(["open", "-a", app])` |

> **Note:** The system automatically detects the operating system it is running on and activates the appropriate driver.
