# ============================================================
# command_handler.py
# Ghost Interface Projesi — Görev 3: Sistem Entegrasyonu
# Sorumlu / Owner: Üye 3 (Dilara)
# ============================================================

import pyautogui
import keyboard
import os
import subprocess
import json
import platform
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CommandHandler")

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01
PERFORMANCE_THRESHOLD_MS = 100


class CommandHandler:

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.command_map = {
            "mouse_move":  self._mouse_move,
            "left_click":  self._left_click,
            "volume_up":   self._volume_up,
            "volume_down": self._volume_down,
            "zoom_in":     self._zoom_in,
            "zoom_out":    self._zoom_out,
            "open_app":    self._open_app,
            "next_page":   self._next_page,
            "prev_page":   self._prev_page,
        }
        self.os_name = platform.system()
        logger.info(f"CommandHandler başlatıldı — İşletim Sistemi: {self.os_name}")

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info("config.json başarıyla yüklendi.")
            return config
        except FileNotFoundError:
            logger.warning("config.json bulunamadı, varsayılan ayarlar kullanılıyor.")
            return {"gestures": {}, "app_to_open": "notepad", "volume_step": 5, "zoom_step": 0.1}
        except json.JSONDecodeError as e:
            logger.error(f"config.json okunamadı: {e}")
            return {"gestures": {}, "app_to_open": "notepad", "volume_step": 5, "zoom_step": 0.1}

    def execute(self, gesture_name: str, hand_coords: dict = None):
        if gesture_name is None:
            return
        gesture_name = gesture_name.strip().lower()
        command_name = self.config["gestures"].get(gesture_name)
        if not command_name:
            logger.debug(f"Tanımsız jest: {gesture_name}")
            return
        command_fn = self.command_map.get(command_name)
        if not command_fn:
            logger.error(f"Komut fonksiyonu bulunamadı: {command_name}")
            return
        start_time = time.perf_counter()
        try:
            logger.info(f"Jest: {gesture_name} → Komut: {command_name}")
            command_fn(hand_coords)
        except Exception as e:
            logger.error(f"Komut hatası: {command_name} — {e}")
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        if elapsed_ms > PERFORMANCE_THRESHOLD_MS:
            logger.warning(f"⚠ Performans aşıldı: {command_name} → {elapsed_ms:.1f}ms")

    def _mouse_move(self, hand_coords: dict = None):
        if not hand_coords:
            return
        try:
            screen_w, screen_h = pyautogui.size()
            target_x = int(hand_coords.get("x", 0.5) * screen_w)
            target_y = int(hand_coords.get("y", 0.5) * screen_h)
            pyautogui.moveTo(target_x, target_y, duration=0)
        except Exception as e:
            logger.error(f"Fare hareketi başarısız: {e}")

    def _left_click(self, hand_coords: dict = None):
        try:
            pyautogui.click()
            logger.info("Sol tıklama gerçekleşti.")
        except Exception as e:
            logger.error(f"Sol tıklama başarısız: {e}")

    def _volume_up(self, hand_coords: dict = None):
        step = self.config.get("volume_step", 5)
        try:
            if self.os_name == "Windows":
                for _ in range(step):
                    keyboard.send("volume up")
            elif self.os_name == "Linux":
                os.system(f"amixer -D pulse sset Master {step}%+")
            elif self.os_name == "Darwin":
                os.system(f"osascript -e 'set volume output volume (output volume of (get volume settings) + {step})'")
            logger.info(f"Ses {step} adım artırıldı.")
        except Exception as e:
            logger.error(f"Ses artırma başarısız: {e}")

    def _volume_down(self, hand_coords: dict = None):
        step = self.config.get("volume_step", 5)
        try:
            if self.os_name == "Windows":
                for _ in range(step):
                    keyboard.send("volume down")
            elif self.os_name == "Linux":
                os.system(f"amixer -D pulse sset Master {step}%-")
            elif self.os_name == "Darwin":
                os.system(f"osascript -e 'set volume output volume (output volume of (get volume settings) - {step})'")
            logger.info(f"Ses {step} adım azaltıldı.")
        except Exception as e:
            logger.error(f"Ses azaltma başarısız: {e}")

    def _zoom_in(self, hand_coords: dict = None):
        try:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(500)
            pyautogui.keyUp('ctrl')
            logger.info("Zoom in (Ctrl + Scroll Up).")
        except Exception as e:
            logger.error(f"Zoom in başarısız: {e}")

    def _zoom_out(self, hand_coords: dict = None):
        try:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(-500)
            pyautogui.keyUp('ctrl')
            logger.info("Zoom out (Ctrl + Scroll Down).")
        except Exception as e:
            logger.error(f"Zoom out başarısız: {e}")

    def _open_app(self, hand_coords: dict = None):
        app = self.config.get("app_to_open", "notepad")
        try:
            if self.os_name == "Windows":
                subprocess.Popen(app, shell=True)
            elif self.os_name == "Linux":
                subprocess.Popen([app])
            elif self.os_name == "Darwin":
                subprocess.Popen(["open", "-a", app])
            logger.info(f"Uygulama başlatıldı: {app}")
        except Exception as e:
            logger.error(f"Uygulama açma başarısız: {e}")

    def _next_page(self, hand_coords: dict = None):
        try:
            keyboard.send("right")
            logger.info("Sonraki sayfa (Right).")
        except Exception as e:
            logger.error(f"Sonraki sayfa hatası: {e}")

    def _prev_page(self, hand_coords: dict = None):
        try:
            keyboard.send("left")
            logger.info("Önceki sayfa (Left).")
        except Exception as e:
            logger.error(f"Önceki sayfa hatası: {e}")


if __name__ == "__main__":
    handler = CommandHandler()
    print("\n" + "=" * 60)
    print("   Ghost Interface — Command Handler Manuel Test")
    print("=" * 60)
    test_gestures = [
        ("thumb_up",   None),
        ("thumb_down", None),
        ("pinch_out",  None),
        ("pinch_in",   None),
        ("open_palm",  {"x": 0.5, "y": 0.5}),
        ("fist",       None),
        ("swipe_right",None),
        ("swipe_left", None),
    ]
    for gesture, coords in test_gestures:
        print(f"\n--- Jest test: {gesture} ---")
        handler.execute(gesture, coords)
    print("\n" + "=" * 60)
    print("   Tüm testler tamamlandı.")
    print("=" * 60)
