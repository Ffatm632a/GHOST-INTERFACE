# ============================================================
# command_handler.py
# Ghost Interface Projesi — Görev 3: Sistem Entegrasyonu
# Sorumlu: Üye 3 (Dilara)
# Açıklama: Jest adlarını alıp bilgisayar komutlarına çevirir.
#
# ── Entegrasyon Notu (Sprint 2 Uyumu) ──────────────────────
# Üye 2 (Ceylin) — gesture_engine.py — jest adlarını BÜYÜK
# HARF döndürmektedir (ör: "OPEN_PALM", "FIST", "POINTING_UP").
# execute() metoduna .lower().strip() normalizasyonu eklenmiştir.
# Bu "Defensive Programming" (savunmacı programlama) prensibidir:
# kendi modülün girişini sen denetlersin, başkasına körü körüne
# güvenmezsin. config.json her zaman küçük harf tutar.
# ============================================================

import pyautogui          # Fare ve klavye kontrolü için
import keyboard           # Klavye tuşu simülasyonu için
import os                 # İşletim sistemi komutları için
import subprocess         # Harici uygulama başlatmak için
import json               # config.json okumak için
import platform           # İşletim sistemini tespit etmek için
import logging            # Hata ve işlem kayıtları için
import time               # Performans ölçümü için

# ── Loglama ayarları ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("CommandHandler")

# ── PyAutoGUI güvenlik ayarları ───────────────────────────
pyautogui.FAILSAFE = True   # Fare köşeye gidince dur (güvenlik)
pyautogui.PAUSE = 0.01      # Komutlar arası minimum bekleme (saniye)

# ── Performans eşiği (milisaniye) ─────────────────────────
PERFORMANCE_THRESHOLD_MS = 100


class CommandHandler:
    """
    Jest adını alıp ilgili sistem komutunu çalıştıran ana sınıf.
    config.json dosyasından jest-komut eşleşmelerini okur.
    """

    def __init__(self, config_path: str = "config.json"):
        # Yapılandırma dosyasını yükle
        self.config = self._load_config(config_path)
        # Jest → komut fonksiyonu eşleştirme sözlüğü
        self.command_map = {
            "mouse_move":  self._mouse_move,
            "left_click":  self._left_click,
            "volume_up":   self._volume_up,
            "volume_down": self._volume_down,
            "zoom_in":     self._zoom_in,
            "zoom_out":    self._zoom_out,
            "open_app":    self._open_app,
        }
        # İşletim sistemini bir kez tespit et — tekrar sorulmaz
        self.os_name = platform.system()   # "Windows", "Linux", "Darwin"
        logger.info(f"CommandHandler başlatıldı — İşletim Sistemi: {self.os_name}")

    # ── Yapılandırma Yükleme ──────────────────────────────
    def _load_config(self, path: str) -> dict:
        """config.json dosyasını okur ve dict olarak döner."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info("config.json başarıyla yüklendi.")
            return config
        except FileNotFoundError:
            # Dosya yoksa varsayılan değerlerle devam et — sistem çökmez
            logger.warning("config.json bulunamadı, varsayılan ayarlar kullanılıyor.")
            return {
                "gestures": {},
                "app_to_open": "notepad",
                "volume_step": 5,
                "zoom_step": 0.1
            }
        except json.JSONDecodeError as e:
            # JSON bozuksa da varsayılan değerlere düş
            logger.error(f"config.json okunamadı (JSON hatası): {e}")
            return {
                "gestures": {},
                "app_to_open": "notepad",
                "volume_step": 5,
                "zoom_step": 0.1
            }

    # ── Ana Çalıştırıcı ───────────────────────────────────
    def execute(self, gesture_name: str, hand_coords: dict = None):
        """
        Dışarıdan çağrılan tek giriş noktası.
        gesture_name : gesture_engine.py'den gelen jest adı (str)
        hand_coords  : el landmark koordinatları (dict, isteğe bağlı)

        Performans: her komut 100ms altında tamamlanmalıdır.
        Sistem güvenliği: bilinmeyen jest gelirse sessizce geçilir.

        ── Uyumluluk Katmanı (Sprint 2) ────────────────────────
        Üye 2 (Ceylin / gesture_engine.py) jest adlarını BÜYÜK
        HARF döndürmektedir. Burada normalize ediyoruz:
          "OPEN_PALM" → "open_palm"  (config.json ile uyumlu)
          "FIST"      → "fist"
        Bu sayede config.json değişmez, her modül kendi formatında
        çalışabilir ve entegrasyon sorunsuz olur.
        """
        # ── GİRİŞ NORMALİZASYONU ────────────────────────────
        # Gelen jest adını küçük harfe çevir ve baş/sondaki boşlukları temizle.
        # Üye 2'nin "OPEN_PALM" gönderdiğini, Üye 4'ün "open_palm " gönderdiğini
        # varsayabiliriz — hepsini aynı formata getiriyoruz.
        if gesture_name is None:
            logger.debug("execute(): gesture_name None geldi, atlanıyor.")
            return
        gesture_name = gesture_name.strip().lower()   # "OPEN_PALM" → "open_palm"

        # Config'den jest → komut adını bul
        command_name = self.config["gestures"].get(gesture_name)

        if not command_name:
            # Tanımsız jest — sessizce geç, debug log yaz
            logger.debug(f"Tanımsız jest alındı: {gesture_name}")
            return

        # Komut fonksiyonunu haritadan al
        command_fn = self.command_map.get(command_name)

        if not command_fn:
            logger.error(f"Komut fonksiyonu bulunamadı: {command_name}")
            return

        # ── Performans ölçümü başlat ──────────────────────
        start_time = time.perf_counter()

        try:
            logger.info(f"Jest: {gesture_name} → Komut: {command_name}")
            command_fn(hand_coords)
        except Exception as e:
            # Herhangi bir komut hatası sistemin çökmesine neden olmasın
            logger.error(f"Komut çalıştırılırken hata: {command_name} — {e}")

        # ── Performans ölçümü bitir ve değerlendir ────────
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        if elapsed_ms > PERFORMANCE_THRESHOLD_MS:
            logger.warning(
                f"⚠ Performans aşıldı: {command_name} → {elapsed_ms:.1f}ms "
                f"(eşik: {PERFORMANCE_THRESHOLD_MS}ms)"
            )
        else:
            logger.debug(f"✓ Komut süresi: {command_name} → {elapsed_ms:.1f}ms")

    # ── Fare Hareketi ─────────────────────────────────────
    def _mouse_move(self, hand_coords: dict = None):
        """
        El koordinatlarına göre fare imlecini hareket ettirir.
        hand_coords içinde 'x' ve 'y' normalize değerleri (0.0–1.0) beklenir.
        Üye 1'in hand_detector.py'si bu formatı sağlamalıdır.
        """
        if not hand_coords:
            # Koordinat gelmezse fareyi hareket ettirme
            logger.debug("_mouse_move: koordinat bilgisi yok, atlanıyor.")
            return

        try:
            # Ekran boyutunu al (çözünürlüğe uygun ölçekleme için)
            screen_w, screen_h = pyautogui.size()

            # Gelen koordinatlar 0.0–1.0 aralığında normalize değer varsayılır
            norm_x = hand_coords.get("x", 0.5)
            norm_y = hand_coords.get("y", 0.5)

            # Normalize koordinatı piksel koordinatına çevir
            target_x = int(norm_x * screen_w)
            target_y = int(norm_y * screen_h)

            # Fareyi hedefe taşı (duration=0 → anlık hareket, gecikme yok)
            pyautogui.moveTo(target_x, target_y, duration=0)

        except Exception as e:
            logger.error(f"Fare hareketi başarısız: {e}")

    # ── Sol Tıklama ───────────────────────────────────────
    def _left_click(self, hand_coords: dict = None):
        """Yumruk (fist) jestiyle mevcut fare konumunda sol tıklama yapar."""
        try:
            pyautogui.click()
            logger.info("Sol tıklama gerçekleşti.")
        except Exception as e:
            logger.error(f"Sol tıklama başarısız: {e}")

    # ── Ses Artırma ───────────────────────────────────────
    def _volume_up(self, hand_coords: dict = None):
        """
        Başparmak yukarı (thumb_up) jestiyle sistem sesini artırır.
        volume_step değeri config.json'dan okunur.
        Platform tespiti: Windows / Linux / macOS desteği.
        """
        step = self.config.get("volume_step", 5)  # Kaç adım artacak

        try:
            if self.os_name == "Windows":
                # Windows'ta klavye kısayoluyla ses artır
                for _ in range(step):
                    keyboard.send("volume up")

            elif self.os_name == "Linux":
                # Linux'ta amixer komutuyla PulseAudio sesini artır
                os.system(f"amixer -D pulse sset Master {step}%+")

            elif self.os_name == "Darwin":
                # macOS'ta osascript ile AppleEvent ses artır
                os.system(
                    f"osascript -e 'set volume output volume "
                    f"(output volume of (get volume settings) + {step})'"
                )

            logger.info(f"Ses {step} adım artırıldı.")

        except Exception as e:
            logger.error(f"Ses artırma başarısız: {e}")

    # ── Ses Azaltma ───────────────────────────────────────
    def _volume_down(self, hand_coords: dict = None):
        """
        Başparmak aşağı (thumb_down) jestiyle sistem sesini azaltır.
        volume_step değeri config.json'dan okunur.
        Platform tespiti: Windows / Linux / macOS desteği.
        """
        step = self.config.get("volume_step", 5)

        try:
            if self.os_name == "Windows":
                # Windows'ta klavye kısayoluyla ses azalt
                for _ in range(step):
                    keyboard.send("volume down")

            elif self.os_name == "Linux":
                # Linux'ta amixer komutuyla PulseAudio sesini azalt
                os.system(f"amixer -D pulse sset Master {step}%-")

            elif self.os_name == "Darwin":
                # macOS'ta osascript ile AppleEvent ses azalt
                os.system(
                    f"osascript -e 'set volume output volume "
                    f"(output volume of (get volume settings) - {step})'"
                )

            logger.info(f"Ses {step} adım azaltıldı.")

        except Exception as e:
            logger.error(f"Ses azaltma başarısız: {e}")

    # ── Zum Yakınlaştırma ─────────────────────────────────
    def _zoom_in(self, hand_coords: dict = None):
        """
        İki parmak açma (pinch_out) jestiyle ekranı yakınlaştırır.
        Ctrl + '+' kısayoluyla tarayıcı ve metin editörlerinde çalışır.
        """
        try:
            pyautogui.hotkey("ctrl", "+")
            logger.info("Zoom in uygulandı (Ctrl++).")
        except Exception as e:
            logger.error(f"Zoom in başarısız: {e}")

    # ── Zum Uzaklaştırma ──────────────────────────────────
    def _zoom_out(self, hand_coords: dict = None):
        """
        İki parmak kapama (pinch_in) jestiyle ekranı uzaklaştırır.
        Ctrl + '-' kısayoluyla tarayıcı ve metin editörlerinde çalışır.
        """
        try:
            pyautogui.hotkey("ctrl", "-")
            logger.info("Zoom out uygulandı (Ctrl+-).")
        except Exception as e:
            logger.error(f"Zoom out başarısız: {e}")

    # ── Uygulama Açma ─────────────────────────────────────
    def _open_app(self, hand_coords: dict = None):
        """
        Yumruk açma (fist_open) jestiyle config.json'daki uygulamayı başlatır.
        subprocess.Popen kullanılır: os.system'e göre daha güvenli,
        shell injection riski düşük, çıktı yakalanabilir.
        """
        app = self.config.get("app_to_open", "notepad")

        try:
            if self.os_name == "Windows":
                # Windows'ta shell=True ile PATH içindeki uygulamayı bul
                subprocess.Popen(app, shell=True)

            elif self.os_name == "Linux":
                # Linux'ta doğrudan process aç
                subprocess.Popen([app])

            elif self.os_name == "Darwin":
                # macOS'ta 'open -a' ile Application klasöründen bul
                subprocess.Popen(["open", "-a", app])

            logger.info(f"Uygulama başlatıldı: {app}")

        except FileNotFoundError:
            # Uygulama kurulu değil veya PATH'te bulunamadı
            logger.error(
                f"Uygulama açılamadı: '{app}' — "
                "Kurulu değil veya sistem PATH'inde yok."
            )
        except Exception as e:
            logger.error(f"Uygulama açma başarısız: {e}")


# ── Doğrudan çalıştırma — manuel test bloğu ───────────────
if __name__ == "__main__":
    handler = CommandHandler()

    print("\n" + "=" * 60)
    print("   Ghost Interface — Command Handler Manuel Test")
    print("=" * 60)

    # Her komutu sırayla dene
    test_gestures = [
        ("thumb_up",   None),
        ("thumb_down", None),
        ("pinch_out",  None),
        ("pinch_in",   None),
        ("open_palm",  {"x": 0.5, "y": 0.5}),
        ("fist",       None),
        ("fist_open",  None),
        ("bilinmeyen", None),   # Tanımsız jest — sistem çökmemeli
    ]

    for gesture, coords in test_gestures:
        print(f"\n--- Jest test: {gesture} ---")
        handler.execute(gesture, coords)

    print("\n" + "=" * 60)
    print("   Tüm testler tamamlandı.")
    print("=" * 60)
