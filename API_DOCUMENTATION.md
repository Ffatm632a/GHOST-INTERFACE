# GHOST INTERFACE API Documentation

## 1. Overview

GHOST INTERFACE is a local Flask-based control panel for gesture-driven computer interaction. It combines webcam input, MediaPipe hand landmark detection, gesture classification, and system command execution.

The public API is intentionally small:

- It serves the web dashboard.
- It streams the annotated camera feed as MJPEG.
- It exposes the latest detected gesture and recent gesture events.
- It checks whether the default camera can be opened.

The application is designed to run locally on the user's machine because it can trigger OS-level actions such as mouse movement, clicking, volume changes, zoom shortcuts, and keyboard navigation.

## 2. Base URL

Default local server:

```text
http://127.0.0.1:5000
```

The server is started from `web_app.py`:

```bash
python web_app.py
```

Runtime defaults:

| Setting | Value |
|---|---|
| Host | `127.0.0.1` |
| Port | `5000` |
| Debug mode | `false` |
| Reloader | `false` |

## 3. Authentication

No authentication is implemented.

Because the application can execute local system commands, it should only be exposed on a trusted local machine. Do not bind it to a public network interface without adding authentication and command-safety controls.

## 4. Content Types

| Resource | Content Type |
|---|---|
| Dashboard page | `text/html` |
| API responses | `application/json` |
| Camera stream | `multipart/x-mixed-replace; boundary=frame` |
| Stream frames | JPEG image bytes |

## 5. Endpoints

### 5.1 `GET /`

Returns the main GHOST INTERFACE dashboard.

The dashboard lets a user select a local document or image, start the gesture interface, view the live camera feed, and see detected gesture feedback.

**Request**

```http
GET /
```

**Response**

```http
200 OK
Content-Type: text/html
```

**Example**

```bash
curl http://127.0.0.1:5000/
```

**Notes**

- The page loads `static/css/style.css` and `static/js/main.js`.
- The frontend starts the live video feed by creating an image element with `src="/video_feed"`.
- The frontend polls `/api/status` every 500 ms while the dashboard is active.

---

### 5.2 `GET /video_feed`

Streams annotated webcam frames using MJPEG.

Each request opens a new `CameraStream`, reads frames from camera index `0`, detects hand landmarks, draws landmark/status overlays, updates the latest gesture state, and yields JPEG frames in a multipart response.

**Request**

```http
GET /video_feed
```

**Response**

```http
200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame
```

Each part has this structure:

```http
--frame
Content-Type: image/jpeg

<jpeg-bytes>
```

**Example HTML Usage**

```html
<img src="/video_feed" alt="Live camera feed">
```

**Example Fetch Usage**

MJPEG streams are usually consumed by an `<img>` tag rather than `fetch`, because the response is continuous.

**Camera Failure Behavior**

If the webcam cannot be opened, the stream returns a generated fallback JPEG frame containing a camera-not-found message instead of crashing the route.

**Side Effects**

While the stream is active, the server may execute commands when a recognized gesture passes its cooldown check.

Pipeline:

```text
Camera frame -> HandDetector -> GestureEngine -> CommandHandler -> event log
```

---

### 5.3 `GET /api/status`

Returns the latest detected gesture and a recent event log.

The frontend uses this endpoint to update the "Last Gesture" panel and display gesture feedback.

**Request**

```http
GET /api/status
```

**Response**

```http
200 OK
Content-Type: application/json
```

**Response Body**

```json
{
  "gesture": "open_palm",
  "log": [
    {
      "time": "14:32:08",
      "gesture": "open_palm"
    }
  ]
}
```

**Fields**

| Field | Type | Description |
|---|---|---|
| `gesture` | string | Latest gesture name. Defaults to `unknown` before a gesture is detected. |
| `log` | array | Most recent gesture execution events, newest first. |
| `log[].time` | string | Local server time in `HH:MM:SS` format. |
| `log[].gesture` | string | Gesture name that triggered a command. |

**Gesture Values**

Possible values produced by the current gesture engine:

| Gesture | Meaning | Command Mapping |
|---|---|---|
| `unknown` | No recognizable hand gesture | No command |
| `open_palm` | Open hand | `mouse_move` |
| `fist` | Closed fist | `left_click` |
| `thumb_up` | Thumb up | `volume_up` |
| `thumb_down` | Thumb down | `volume_down` |
| `pinch_out` | Pinch-open gesture | `zoom_in` |
| `pinch_in` | Pinch-close gesture | `zoom_out` |
| `pointing_up` | Index finger raised | `left_click` |
| `swipe_right` | Open palm moved right | `next_page` |
| `swipe_left` | Open palm moved left | `prev_page` |

**Example**

```bash
curl http://127.0.0.1:5000/api/status
```

**Example Response**

```json
{
  "gesture": "thumb_up",
  "log": [
    {
      "time": "16:41:20",
      "gesture": "thumb_up"
    },
    {
      "time": "16:41:13",
      "gesture": "open_palm"
    }
  ]
}
```

**Log Behavior**

- The server stores up to 30 gesture events internally.
- The API returns the latest 15 events.
- The returned list is reversed so the newest event appears first.

---

### 5.4 `GET /api/camera/status`

Checks whether camera index `0` can be opened.

This endpoint creates a short-lived OpenCV `VideoCapture`, checks `isOpened()`, releases it, and returns the result.

**Request**

```http
GET /api/camera/status
```

**Response**

```http
200 OK
Content-Type: application/json
```

**Response Body**

```json
{
  "ok": true
}
```

**Fields**

| Field | Type | Description |
|---|---|---|
| `ok` | boolean | `true` when the default webcam can be opened; otherwise `false`. |

**Example**

```bash
curl http://127.0.0.1:5000/api/camera/status
```

**Example Response**

```json
{
  "ok": false
}
```

## 6. Internal Data Contracts

These contracts are not exposed as standalone HTTP endpoints, but they define how the API behaves internally.

### 6.1 Gesture Detection Result

`GestureEngine.detect_gesture(landmarks)` returns:

```json
{
  "gesture": "open_palm",
  "confidence": 1.0,
  "hand_coords": {
    "x": 0.45,
    "y": 0.30
  }
}
```

| Field | Type | Description |
|---|---|---|
| `gesture` | string | Detected gesture name. |
| `confidence` | number | Current implementation returns `1.0` for recognized gesture states and `0.0` for no landmarks. |
| `hand_coords` | object or null | Smoothed normalized hand center coordinates. |
| `hand_coords.x` | number | Horizontal coordinate in normalized screen space, usually `0.0` to `1.0`. |
| `hand_coords.y` | number | Vertical coordinate in normalized screen space, usually `0.0` to `1.0`. |

No-landmark result:

```json
{
  "gesture": "unknown",
  "confidence": 0.0,
  "hand_coords": null
}
```

### 6.2 Command Execution Input

`CommandHandler.execute(gesture_name, hand_coords)` accepts:

| Parameter | Type | Required | Description |
|---|---|---:|---|
| `gesture_name` | string | Yes | Gesture name. The value is normalized with `strip().lower()`. |
| `hand_coords` | object or null | No | Normalized coordinates used by mouse movement. |

Example:

```python
handler.execute("open_palm", {"x": 0.5, "y": 0.3})
```

Unknown gestures are ignored silently.

## 7. Gesture Cooldowns

The web pipeline applies cooldowns before executing commands. This prevents repeated high-frequency triggers from continuous video frames.

| Gesture | Cooldown |
|---|---:|
| `open_palm` | `0` seconds |
| `swipe_right` | `0.8` seconds |
| `swipe_left` | `0.8` seconds |
| `thumb_up` | `0.8` seconds |
| `thumb_down` | `0.8` seconds |
| `pinch_in` | `0.8` seconds |
| `pinch_out` | `0.8` seconds |
| `fist` | `0.5` seconds |
| `pointing_up` | `0.5` seconds |
| Any other gesture | `0.8` seconds |

## 8. Configuration

Gesture-to-command behavior is controlled by `config.json`.

Current configuration:

```json
{
  "gestures": {
    "open_palm": "mouse_move",
    "fist": "left_click",
    "thumb_up": "volume_up",
    "thumb_down": "volume_down",
    "pinch_out": "zoom_in",
    "pinch_in": "zoom_out",
    "pointing_up": "left_click",
    "swipe_right": "next_page",
    "swipe_left": "prev_page"
  },
  "app_to_open": "notepad",
  "volume_step": 5,
  "zoom_step": 0.1
}
```

Supported command names:

| Command | Behavior |
|---|---|
| `mouse_move` | Moves the mouse to normalized hand coordinates. |
| `left_click` | Performs a left mouse click. |
| `volume_up` | Increases system volume. |
| `volume_down` | Decreases system volume. |
| `zoom_in` | Sends `Ctrl` + `+`. |
| `zoom_out` | Sends `Ctrl` + `-`. |
| `open_app` | Opens the configured application. |
| `next_page` | Sends the right-arrow key. |
| `prev_page` | Sends the left-arrow key. |

Note: `open_app` exists in the command handler, but the current `config.json` does not map any gesture to it.

## 9. Platform Behavior

| Command Area | Windows | Linux | macOS |
|---|---|---|---|
| Volume up/down | `keyboard.send("volume up/down")` repeated by `volume_step` | `amixer -D pulse sset Master` | `osascript` volume command |
| Open app | `subprocess.Popen(app, shell=True)` | `subprocess.Popen([app])` | `open -a <app>` |
| Mouse and zoom | `pyautogui` | `pyautogui` | `pyautogui` |

## 10. Error Handling

| Area | Behavior |
|---|---|
| Missing `config.json` | Falls back to empty gesture mappings, `notepad`, `volume_step=5`, and `zoom_step=0.1`. |
| Invalid `config.json` | Uses the same fallback defaults. |
| Unknown gesture | Ignored; no exception is raised. |
| Missing hand coordinates for mouse movement | Mouse movement is skipped. |
| Webcam cannot open in `/video_feed` | A fallback JPEG frame is returned. |
| Webcam cannot open in `/api/camera/status` | Returns `{ "ok": false }`. |
| Command execution error | Logged by `CommandHandler`; the server route continues running. |

## 11. Frontend Integration

The existing frontend uses the API as follows:

```javascript
const img = document.createElement('img');
img.src = '/video_feed';
```

```javascript
setInterval(async () => {
  const response = await fetch('/api/status');
  const data = await response.json();
  const gesture = data.gesture;
}, 500);
```

Recommended UI behavior:

- Use `/api/camera/status` before starting a session if you want to warn the user about camera availability.
- Render `/video_feed` through an `<img>` element.
- Poll `/api/status` at moderate intervals, such as 500 ms.
- Treat `unknown` as an idle/no-signal state.

## 12. Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Server

```bash
python web_app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Run Tests

```bash
pytest
```

The test suite focuses mainly on command handling and gesture-to-command integration.

## 13. Implementation Source Map

| Concern | File |
|---|---|
| Flask routes and shared API state | `web_app.py` |
| Camera frame generation and MJPEG output | `camera_stream.py` |
| MediaPipe hand landmark detection | `hand_detector.py` |
| Gesture classification | `gesture_engine.py` |
| Gesture-to-command execution | `command_handler.py` |
| Runtime gesture mapping | `config.json` |
| Dashboard template | `templates/index.html` |
| Frontend API polling | `static/js/main.js` |

## 14. Current API Limitations

- The API has no authentication or authorization.
- There are no POST endpoints for changing configuration at runtime.
- The video stream is tied to camera index `0`.
- The status API only reports the latest gesture and recent gesture events; it does not expose FPS, landmark count, or stream health.
- Command execution is coupled to the active video stream. If `/video_feed` is not being consumed, gesture detection and command execution are not running through the web pipeline.
- `/api/status` returns in-memory state only. State resets when the Flask process restarts.

## 15. Recommended Future API Additions

These additions would make the API easier to operate and test without changing the current public behavior:

| Endpoint | Purpose |
|---|---|
| `GET /api/config` | Return active gesture-command mappings. |
| `PUT /api/config` | Update mappings and settings safely at runtime. |
| `POST /api/commands/test` | Trigger a command in a controlled test mode. |
| `GET /api/stream/status` | Return FPS, frame count, landmark count, and stream running state. |
| `POST /api/session/start` | Start detection independently from the browser image stream. |
| `POST /api/session/stop` | Stop detection and release camera resources explicitly. |

