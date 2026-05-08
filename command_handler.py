# ============================================================
# command_handler.py
# Ghost Interface Projesi — Görev 3: Sistem Entegrasyonu
# Ghost Interface Project — Task 3: System Integration
#
# Sorumlu / Owner: Üye 3 (Dilara)
# Branch: Dilara
#
# TR: Bu dosya, el hareketlerini (jestleri) bilgisayar komutlarına
#     çevirir. Örneğin avucunu açarsan fare hareket eder,
#     yumruk yaparsan tıklama olur.
#
# EN: This file converts hand gestures into real computer commands.
#     For example, open palm moves the mouse, fist does a click.
#
# ── Entegrasyon Notu / Integration Note ─────────────────────
# TR: Zeynep kamera ve el tespitini (capture.py, hand_detector.py),
#     Ceylin jest analizi motorunu (gesture_engine.py) yazdı.
#     Bu dosya onların çıktısını alıp bilgisayara komut veriyor.
#
# EN: Zeynep wrote camera & hand detection (capture.py, hand_detector.py),
#     Ceylin wrote gesture analysis (gesture_engine.py).
#     This file takes their output and executes system commands.
#
# TR: Ceylin'in çıktı formatı (dictionary):
#     {"gesture": "open_palm", "confidence": 1.0, "hand_coords": {"x": 0.5, "y": 0.3}}
#
# EN: Ceylin's output format (dictionary):
#     {"gesture": "open_palm", "confidence": 1.0, "hand_coords": {"x": 0.5, "y": 0.3}}
# ============================================================

# ── Kütüphaneler / Libraries ────────────────────────────────
# TR: Projede kullandığımız dış kütüphaneleri içe aktarıyoruz.
# EN: Importing external libraries used in this project.

import pyautogui          # TR: Fare ve klavye kontrolü / EN: Mouse and keyboard control
import keyboard           # TR: Klavye tuşu simülasyonu / EN: Keyboard key simulation
import os                 # TR: İşletim sistemi komutları / EN: OS-level commands
import subprocess         # TR: Harici uygulama başlatma / EN: Launch external applications
import json               # TR: config.json dosyasını okuma / EN: Read config.json file
import platform           # TR: İşletim sistemi tespiti / EN: Detect operating system
import logging            # TR: Hata ve işlem kayıtları / EN: Error and event logging
import time               # TR: Performans ölçümü / EN: Performance measurement

# ── Loglama Ayarları / Logging Configuration ─────────────────
# TR: Sistemde neler olduğunu takip etmek için log (kayıt) sistemi kuruyoruz.
#     Her komut çalıştığında veya hata oluştuğunda buraya yazılır.
# EN: Setting up a logging system to track what happens in the system.
#     Every command execution or error gets recorded here.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("CommandHandler")

# ── PyAutoGUI Güvenlik Ayarları / PyAutoGUI Safety Settings ──
# TR: FAILSAFE = True → Fare ekranın sol üst köşesine giderse program durur.
#     Bu bir güvenlik önlemidir, kontrol kaybını engeller.
# EN: FAILSAFE = True → If mouse goes to top-left corner, program stops.
#     This is a safety measure to prevent loss of control.
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01      # TR: Komutlar arası bekleme (saniye) / EN: Delay between commands (seconds)

# ── Performans Eşiği / Performance Threshold ─────────────────
# TR: Her komut 100 milisaniyeden kısa sürmeli. Aşarsa uyarı verilir.
# EN: Each command should complete under 100ms. A warning is logged if exceeded.
PERFORMANCE_THRESHOLD_MS = 100


class CommandHandler:
    """
    TR: Ana sınıf — jest adını alır, config.json'a bakar, doğru komutu çalıştırır.
    EN: Main class — takes gesture name, checks config.json, runs the correct command.
    """

    def __init__(self, config_path: str = "config.json"):
        """
        TR: Sınıf oluşturulduğunda çalışır. Config dosyasını yükler,
            komut haritasını kurar ve işletim sistemini tespit eder.
        EN: Runs when class is created. Loads config file,
            sets up command map, and detects operating system.
        """
        # TR: Ayar dosyasını yükle / EN: Load configuration file
        self.config = self._load_config(config_path)

        # TR: Jest → komut fonksiyonu eşleştirme sözlüğü
        #     Config'de "mouse_move" yazıyorsa, _mouse_move fonksiyonunu çağır.
        # EN: Gesture → command function mapping dictionary
        #     If config says "mouse_move", call _mouse_move function.
        self.command_map = {
            "mouse_move":  self._mouse_move,
            "left_click":  self._left_click,
            "volume_up":   self._volume_up,
            "volume_down": self._volume_down,
            "zoom_in":     self._zoom_in,
            "zoom_out":    self._zoom_out,
            "open_app":    self._open_app,
        }

        # TR: İşletim sistemini bir kez tespit et (Windows, Linux, macOS)
        # EN: Detect OS once (Windows, Linux, macOS)
        self.os_name = platform.system()
        logger.info(f"CommandHandler başlatıldı — İşletim Sistemi: {self.os_name}")

    # ── Yapılandırma Yükleme / Load Configuration ────────────
    def _load_config(self, path: str) -> dict:
        """
        TR: config.json dosyasını okur. Dosya yoksa veya bozuksa
            varsayılan ayarlarla devam eder — sistem asla çökmez.
        EN: Reads config.json file. If file is missing or corrupted,
            falls back to default settings — system never crashes.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info("config.json başarıyla yüklendi.")
            return config

        except FileNotFoundError:
            # TR: Dosya bulunamadı → varsayılan ayarları kullan
            # EN: File not found → use default settings
            logger.warning("config.json bulunamadı, varsayılan ayarlar kullanılıyor.")
            return {
                "gestures": {},
                "app_to_open": "notepad",
                "volume_step": 5,
                "zoom_step": 0.1
            }

        except json.JSONDecodeError as e:
            # TR: JSON formatı bozuk → varsayılan ayarlara düş
            # EN: JSON format is broken → fall back to defaults
            logger.error(f"config.json okunamadı (JSON hatası): {e}")
            return {
                "gestures": {},
                "app_to_open": "notepad",
                "volume_step": 5,
                "zoom_step": 0.1
            }

    # ══════════════════════════════════════════════════════════
    # ANA ÇALIŞTIRICI / MAIN EXECUTOR
    # ══════════════════════════════════════════════════════════
    def execute(self, gesture_name: str, hand_coords: dict = None):
        """
        TR: Dışarıdan çağrılan TEK giriş noktası.
            Ceylin'in gesture_engine.py'sinden jest adı gelir,
            bu metot config.json'a bakıp doğru komutu çalıştırır.

            Kullanım:
              handler.execute("open_palm", {"x": 0.5, "y": 0.3})

        EN: The ONLY entry point called from outside.
            Gets gesture name from Ceylin's gesture_engine.py,
            looks up config.json and runs the correct command.

            Usage:
              handler.execute("open_palm", {"x": 0.5, "y": 0.3})
        """
        # ── GİRİŞ NORMALİZASYONU / INPUT NORMALIZATION ──────
        # TR: Gelen jest adını küçük harfe çevirip boşlukları temizliyoruz.
        #     Neden? Ceylin "OPEN_PALM" veya "open_palm" gönderebilir.
        #     .lower() ile ikisi de "open_palm" olur → config'le eşleşir.
        #     Buna "Defensive Programming" (savunmacı programlama) denir.
        # EN: Converting gesture name to lowercase and trimming whitespace.
        #     Why? Ceylin might send "OPEN_PALM" or "open_palm".
        #     .lower() makes both "open_palm" → matches config.
        #     This is called "Defensive Programming".
        if gesture_name is None:
            logger.debug("execute(): gesture_name None geldi, atlanıyor.")
            return
        gesture_name = gesture_name.strip().lower()   # "OPEN_PALM" → "open_palm"

        # TR: Config'den jest adına karşılık gelen komut adını bul
        #     Örnek: "open_palm" → "mouse_move"
        # EN: Look up the command name for this gesture in config
        #     Example: "open_palm" → "mouse_move"
        command_name = self.config["gestures"].get(gesture_name)

        if not command_name:
            # TR: Bu jest config'de tanımlı değil → sessizce geç, çökme
            # EN: This gesture is not defined in config → skip silently, don't crash
            logger.debug(f"Tanımsız jest alındı: {gesture_name}")
            return

        # TR: Komut adına karşılık gelen fonksiyonu bul
        #     Örnek: "mouse_move" → self._mouse_move fonksiyonu
        # EN: Find the function for this command name
        #     Example: "mouse_move" → self._mouse_move function
        command_fn = self.command_map.get(command_name)

        if not command_fn:
            logger.error(f"Komut fonksiyonu bulunamadı: {command_name}")
            return

        # ── PERFORMANS ÖLÇÜMÜ BAŞLAT / START PERFORMANCE TIMER ──
        # TR: Komutun ne kadar sürdüğünü ölçüyoruz (100ms altında olmalı)
        # EN: Measuring how long the command takes (should be under 100ms)
        start_time = time.perf_counter()

        try:
            logger.info(f"Jest: {gesture_name} → Komut: {command_name}")
            # TR: Komutu çalıştır! / EN: Execute the command!
            command_fn(hand_coords)
        except Exception as e:
            # TR: Hata olsa bile sistem çökmesin — hatayı logla ve devam et
            # EN: Even if error occurs, don't crash — log it and continue
            logger.error(f"Komut çalıştırılırken hata: {command_name} — {e}")

        # ── PERFORMANS ÖLÇÜMÜ BİTİR / END PERFORMANCE TIMER ──
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if elapsed_ms > PERFORMANCE_THRESHOLD_MS:
            # TR: 100ms'yi aştı → uyarı ver / EN: Exceeded 100ms → warn
            logger.warning(
                f"⚠ Performans aşıldı: {command_name} → {elapsed_ms:.1f}ms "
                f"(eşik: {PERFORMANCE_THRESHOLD_MS}ms)"
            )
        else:
            logger.debug(f"✓ Komut süresi: {command_name} → {elapsed_ms:.1f}ms")

    # ══════════════════════════════════════════════════════════
    # KOMUT FONKSİYONLARI / COMMAND FUNCTIONS
    # TR: Aşağıdaki her fonksiyon bir jest'e karşılık gelir.
    # EN: Each function below corresponds to a gesture.
    # ══════════════════════════════════════════════════════════

    # ── 1. FARE HAREKETİ / MOUSE MOVEMENT ────────────────────
    def _mouse_move(self, hand_coords: dict = None):
        """
        TR: Açık avuç (open_palm) jesti → Fareyi el pozisyonuna taşır.
            Gelen x,y değerleri 0.0-1.0 arasında normalize koordinatlardır.
            Bunları ekran çözünürlüğüne çevirerek fareyi taşıyoruz.
            Kütüphane: pyautogui.moveTo()

        EN: Open palm gesture → Moves mouse to hand position.
            Incoming x,y values are normalized coordinates (0.0-1.0).
            We convert them to screen resolution and move the mouse.
            Library: pyautogui.moveTo()
        """
        if not hand_coords:
            # TR: Koordinat yoksa fareyi hareket ettirme
            # EN: No coordinates → don't move the mouse
            logger.debug("_mouse_move: koordinat bilgisi yok, atlanıyor.")
            return

        try:
            # TR: Ekran boyutunu öğren (örn: 1920x1080)
            # EN: Get screen size (e.g., 1920x1080)
            screen_w, screen_h = pyautogui.size()

            # TR: Normalize koordinatları al (0.0 ile 1.0 arası)
            # EN: Get normalized coordinates (between 0.0 and 1.0)
            norm_x = hand_coords.get("x", 0.5)
            norm_y = hand_coords.get("y", 0.5)

            # TR: Normalize değeri piksel değerine çevir
            #     Örnek: 0.5 × 1920 = 960 piksel (ekranın ortası)
            # EN: Convert normalized value to pixel value
            #     Example: 0.5 × 1920 = 960 pixels (center of screen)
            target_x = int(norm_x * screen_w)
            target_y = int(norm_y * screen_h)

            # TR: Fareyi hedefe taşı (duration=0 → anlık, gecikmesiz)
            # EN: Move mouse to target (duration=0 → instant, no delay)
            pyautogui.moveTo(target_x, target_y, duration=0)

        except Exception as e:
            logger.error(f"Fare hareketi başarısız: {e}")

    # ── 2. SOL TIKLAMA / LEFT CLICK ──────────────────────────
    def _left_click(self, hand_coords: dict = None):
        """
        TR: Yumruk (fist) veya işaret parmağı (pointing_up) jesti →
            Farenin bulunduğu yerde sol tıklama yapar.
            Kütüphane: pyautogui.click()

        EN: Fist or pointing_up gesture →
            Performs a left click at current mouse position.
            Library: pyautogui.click()
        """
        try:
            pyautogui.click()
            logger.info("Sol tıklama gerçekleşti.")
        except Exception as e:
            logger.error(f"Sol tıklama başarısız: {e}")

    # ── 3. SES ARTIRMA / VOLUME UP ───────────────────────────
    def _volume_up(self, hand_coords: dict = None):
        """
        TR: Başparmak yukarı (thumb_up) jesti → Sistem sesini artırır.
            Kaç adım artacağı config.json'daki "volume_step" değerinden okunur.
            Windows'ta keyboard kütüphanesi, Linux'ta amixer, macOS'ta osascript kullanılır.

        EN: Thumb up gesture → Increases system volume.
            Step count is read from "volume_step" in config.json.
            Uses keyboard library on Windows, amixer on Linux, osascript on macOS.
        """
        # TR: Config'den adım sayısını oku (varsayılan: 5)
        # EN: Read step count from config (default: 5)
        step = self.config.get("volume_step", 5)

        try:
            if self.os_name == "Windows":
                # TR: Windows → Her adımda klavye "volume up" tuşunu simüle et
                # EN: Windows → Simulate "volume up" key press for each step
                for _ in range(step):
                    keyboard.send("volume up")

            elif self.os_name == "Linux":
                # TR: Linux → amixer komutuyla PulseAudio sesini artır
                # EN: Linux → Increase PulseAudio volume with amixer command
                os.system(f"amixer -D pulse sset Master {step}%+")

            elif self.os_name == "Darwin":
                # TR: macOS → osascript ile AppleScript üzerinden ses artır
                # EN: macOS → Increase volume via AppleScript using osascript
                os.system(
                    f"osascript -e 'set volume output volume "
                    f"(output volume of (get volume settings) + {step})'"
                )

            logger.info(f"Ses {step} adım artırıldı.")

        except Exception as e:
            logger.error(f"Ses artırma başarısız: {e}")

    # ── 4. SES AZALTMA / VOLUME DOWN ─────────────────────────
    def _volume_down(self, hand_coords: dict = None):
        """
        TR: Başparmak aşağı (thumb_down) jesti → Sistem sesini azaltır.
            Mantık _volume_up ile aynı, sadece yön ters.

        EN: Thumb down gesture → Decreases system volume.
            Same logic as _volume_up, just opposite direction.
        """
        step = self.config.get("volume_step", 5)

        try:
            if self.os_name == "Windows":
                for _ in range(step):
                    keyboard.send("volume down")

            elif self.os_name == "Linux":
                os.system(f"amixer -D pulse sset Master {step}%-")

            elif self.os_name == "Darwin":
                os.system(
                    f"osascript -e 'set volume output volume "
                    f"(output volume of (get volume settings) - {step})'"
                )

            logger.info(f"Ses {step} adım azaltıldı.")

        except Exception as e:
            logger.error(f"Ses azaltma başarısız: {e}")

    # ── 5. YAKINLAŞTIRMA / ZOOM IN ───────────────────────────
    def _zoom_in(self, hand_coords: dict = None):
        """
        TR: Parmak açma (pinch_out) jesti → Ekranı yakınlaştırır.
            Ctrl + '+' kısayolunu simüle eder.
            Tarayıcılarda ve metin editörlerinde çalışır.
            Kütüphane: pyautogui.hotkey()

        EN: Pinch out gesture → Zooms in on screen.
            Simulates Ctrl + '+' shortcut.
            Works in browsers and text editors.
            Library: pyautogui.hotkey()
        """
        try:
            pyautogui.hotkey("ctrl", "+")
            logger.info("Zoom in uygulandı (Ctrl++).")
        except Exception as e:
            logger.error(f"Zoom in başarısız: {e}")

    # ── 6. UZAKLAŞTIRMA / ZOOM OUT ───────────────────────────
    def _zoom_out(self, hand_coords: dict = None):
        """
        TR: Parmak kapama (pinch_in) jesti → Ekranı uzaklaştırır.
            Ctrl + '-' kısayolunu simüle eder.

        EN: Pinch in gesture → Zooms out on screen.
            Simulates Ctrl + '-' shortcut.
        """
        try:
            pyautogui.hotkey("ctrl", "-")
            logger.info("Zoom out uygulandı (Ctrl+-).")
        except Exception as e:
            logger.error(f"Zoom out başarısız: {e}")

    # ── 7. UYGULAMA AÇMA / OPEN APPLICATION ──────────────────
    def _open_app(self, hand_coords: dict = None):
        """
        TR: Yumruk açma (fist_open) jesti → Config'deki uygulamayı başlatır.
            Varsayılan uygulama: notepad (not defteri).
            subprocess.Popen kullanılır çünkü os.system'den daha güvenlidir.
            Kütüphane: subprocess.Popen()

        EN: Fist open gesture → Launches the app defined in config.json.
            Default app: notepad.
            subprocess.Popen is used because it's safer than os.system.
            Library: subprocess.Popen()
        """
        # TR: Açılacak uygulamayı config'den oku / EN: Read app name from config
        app = self.config.get("app_to_open", "notepad")

        try:
            if self.os_name == "Windows":
                # TR: Windows → shell=True ile PATH'teki uygulamayı bul ve aç
                # EN: Windows → Find and open app from PATH using shell=True
                subprocess.Popen(app, shell=True)

            elif self.os_name == "Linux":
                # TR: Linux → Doğrudan process başlat
                # EN: Linux → Start process directly
                subprocess.Popen([app])

            elif self.os_name == "Darwin":
                # TR: macOS → 'open -a' ile Applications klasöründen bul
                # EN: macOS → Find from Applications folder using 'open -a'
                subprocess.Popen(["open", "-a", app])

            logger.info(f"Uygulama başlatıldı: {app}")

        except FileNotFoundError:
            # TR: Uygulama bulunamadı → hata logla, çökme
            # EN: App not found → log error, don't crash
            logger.error(
                f"Uygulama açılamadı: '{app}' — "
                "Kurulu değil veya sistem PATH'inde yok."
            )
        except Exception as e:
            logger.error(f"Uygulama açma başarısız: {e}")


# ══════════════════════════════════════════════════════════════
# MANUEL TEST BLOĞU / MANUAL TEST BLOCK
# TR: Bu kısım sadece dosyayı doğrudan çalıştırınca çalışır.
#     "python command_handler.py" yazınca her komutu sırayla test eder.
# EN: This section only runs when file is executed directly.
#     "python command_handler.py" tests each command one by one.
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    handler = CommandHandler()

    print("\n" + "=" * 60)
    print("   Ghost Interface — Command Handler Manuel Test")
    print("=" * 60)

    # TR: Test edilecek jestler listesi / EN: List of gestures to test
    test_gestures = [
        ("thumb_up",   None),                    # TR: Ses artır / EN: Volume up
        ("thumb_down", None),                    # TR: Ses azalt / EN: Volume down
        ("pinch_out",  None),                    # TR: Yakınlaştır / EN: Zoom in
        ("pinch_in",   None),                    # TR: Uzaklaştır / EN: Zoom out
        ("open_palm",  {"x": 0.5, "y": 0.5}),   # TR: Fare hareket / EN: Mouse move
        ("fist",       None),                    # TR: Sol tıkla / EN: Left click
        ("fist_open",  None),                    # TR: Uygulama aç / EN: Open app
        ("bilinmeyen", None),                    # TR: Tanımsız jest / EN: Unknown gesture
    ]

    for gesture, coords in test_gestures:
        print(f"\n--- Jest test: {gesture} ---")
        handler.execute(gesture, coords)

    print("\n" + "=" * 60)
    print("   Tüm testler tamamlandı. / All tests completed.")
    print("=" * 60)
