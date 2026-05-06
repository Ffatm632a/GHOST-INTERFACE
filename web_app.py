
from flask import Flask, Response, jsonify

from camera_stream import CameraStream


app = Flask(__name__)
camera_stream = CameraStream()


@app.route("/")
def index():
    return """
    <!doctype html>
    <html lang="tr">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>GHOST INTERFACE - Canli Kamera</title>
        <style>
          body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #111827;
            color: #f9fafb;
          }
          main {
            max-width: 1040px;
            margin: 0 auto;
            padding: 24px;
          }
          img {
            width: 100%;
            border: 1px solid #374151;
            background: #000;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>GHOST INTERFACE - Canli Kamera Akisi</h1>
          <img src="/video_feed" alt="Canli kamera akisi">
        </main>
      </body>
    </html>
    """


@app.route("/video_feed")
def video_feed():
    return Response(
        camera_stream.frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/camera/status")
def camera_status():
    return jsonify(camera_stream.status())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
