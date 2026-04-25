# ============================================================
# tests/test_command.py
# Ghost Interface Projesi — Görev 3: Birim Testler
# Sorumlu: Üye 3
# Açıklama: command_handler.py için unittest tabanlı birim testler.
#            pyautogui ve keyboard mock'lanır — gerçek işlem yapılmaz.
# ============================================================

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Üst dizini Python path'ine ekle — command_handler import edilebilsin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from command_handler import CommandHandler


class TestCommandHandler(unittest.TestCase):
    """CommandHandler sınıfı için temel birim testler."""

    def setUp(self):
        """
        Her test metodundan önce çalışır.
        Temiz bir CommandHandler örneği oluşturur.
        """
        self.handler = CommandHandler()

    # ── Sol Tıklama Testi ────────────────────────────────
    @patch("pyautogui.click")
    def test_left_click(self, mock_click):
        """
        Yumruk (fist) jesti sol tıklamayı tetiklemeli.
        pyautogui.click tam olarak bir kez çağrılmalıdır.
        """
        self.handler.execute("fist")
        mock_click.assert_called_once()   # Bir kez çağrıldı mı?

    # ── Fare Hareketi Testi ───────────────────────────────
    @patch("pyautogui.moveTo")
    def test_mouse_move_with_coords(self, mock_move):
        """
        Açık avuç (open_palm) jesti ve koordinat verilince
        pyautogui.moveTo çağrılmalıdır.
        """
        coords = {"x": 0.5, "y": 0.3}
        self.handler.execute("open_palm", coords)
        mock_move.assert_called_once()    # moveTo çağrıldı mı?

    @patch("pyautogui.moveTo")
    def test_mouse_move_without_coords(self, mock_move):
        """
        Koordinat gönderilmezse moveTo çağrılmamalıdır.
        Sistem hata vermeden devam etmelidir.
        """
        self.handler.execute("open_palm", None)
        mock_move.assert_not_called()     # Koordinat yoksa fare hareket etmemeli

    # ── Zoom Testleri ─────────────────────────────────────
    @patch("pyautogui.hotkey")
    def test_zoom_in(self, mock_hotkey):
        """
        Pinch out jesti Ctrl+'+'i tetiklemeli.
        """
        self.handler.execute("pinch_out")
        mock_hotkey.assert_called_with("ctrl", "+")

    @patch("pyautogui.hotkey")
    def test_zoom_out(self, mock_hotkey):
        """
        Pinch in jesti Ctrl+'-'i tetiklemeli.
        """
        self.handler.execute("pinch_in")
        mock_hotkey.assert_called_with("ctrl", "-")

    # ── Tanımsız Jest Testi ───────────────────────────────
    def test_unknown_gesture_no_exception(self):
        """
        Tanımsız jest geldiğinde sistem exception fırlatmamalı,
        sessizce devam etmelidir. (NFR-06: graceful degradation)
        """
        try:
            self.handler.execute("bilinmeyen_jest")
            self.handler.execute("")
            self.handler.execute("xyz_123_invalid")
        except Exception as e:
            self.fail(f"Tanımsız jest exception fırlattı: {e}")

    # ── Config Yükleme Testleri ───────────────────────────
    def test_config_loaded_correctly(self):
        """
        config.json doğru yüklenince gesture eşleşmeleri
        handler içinde bulunabilmelidir.
        """
        # config.json varsa gestures sözlüğü dolu olmalı
        self.assertIn("gestures", self.handler.config)
        self.assertIsInstance(self.handler.config["gestures"], dict)

    def test_default_config_on_missing_file(self):
        """
        config.json bulunamazsa varsayılan değerler kullanılmalı,
        sistem çökmemeli.
        """
        # Var olmayan bir path ile handler oluştur
        handler = CommandHandler(config_path="var_olmayan_dosya.json")
        # Varsayılan değerlerin geldiğini kontrol et
        self.assertEqual(handler.config.get("app_to_open"), "notepad")
        self.assertEqual(handler.config.get("volume_step"), 5)

    # ── Uygulama Açma Testi ───────────────────────────────
    @patch("subprocess.Popen")
    def test_open_app_called(self, mock_popen):
        """
        fist_open jesti subprocess.Popen'ı çağırmalıdır.
        """
        self.handler.execute("fist_open")
        mock_popen.assert_called_once()

    # ── Ses Kontrolü Testleri (Windows) ──────────────────
    @patch("platform.system", return_value="Windows")
    @patch("keyboard.send")
    def test_volume_up_windows(self, mock_send, mock_platform):
        """
        Windows'ta thumb_up jesti keyboard.send('volume up')
        çağırmalıdır.
        """
        # os_name'i Windows olarak zorla
        self.handler.os_name = "Windows"
        self.handler.execute("thumb_up")
        # volume_step=5 olduğu için 5 kez çağrılmalı
        self.assertEqual(mock_send.call_count, 5)

    @patch("platform.system", return_value="Windows")
    @patch("keyboard.send")
    def test_volume_down_windows(self, mock_send, mock_platform):
        """
        Windows'ta thumb_down jesti keyboard.send('volume down')
        çağırmalıdır.
        """
        self.handler.os_name = "Windows"
        self.handler.execute("thumb_down")
        self.assertEqual(mock_send.call_count, 5)

    # ── Performans Testi ──────────────────────────────────
    @patch("pyautogui.click")
    def test_execute_performance(self, mock_click):
        """
        execute() metodu 100ms altında tamamlanmalıdır.
        (NFR: Her komut 100ms altında çalışmalı)
        """
        import time
        start = time.perf_counter()
        self.handler.execute("fist")
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.assertLess(
            elapsed_ms, 100,
            f"execute() 100ms'yi aştı: {elapsed_ms:.1f}ms"
        )


class TestCommandHandlerIntegration(unittest.TestCase):
    """
    Entegrasyon düzeyi testler.
    Üye 2'nin gesture_engine.py'sinden gelecek veri formatı simüle edilir.
    """

    def setUp(self):
        """Her testten önce handler oluştur."""
        self.handler = CommandHandler()

    @patch("pyautogui.hotkey")
    def test_gesture_engine_format_zoom_in(self, mock_hotkey):
        """
        Üye 2'den gelen tam veri formatıyla zoom in testi.
        """
        # gesture_engine.py tarafından dönen örnek veri formatı
        gesture_result = {
            "gesture": "pinch_out",
            "confidence": 0.95,
            "hand_coords": {"x": 0.45, "y": 0.30}
        }
        # Entegrasyon kullanım şekli (main.py'deki gibi)
        self.handler.execute(
            gesture_result["gesture"],
            gesture_result["hand_coords"]
        )
        mock_hotkey.assert_called_with("ctrl", "+")

    @patch("pyautogui.moveTo")
    def test_gesture_engine_format_mouse_move(self, mock_move):
        """
        Üye 2'den gelen tam veri formatıyla fare hareketi testi.
        """
        gesture_result = {
            "gesture": "open_palm",
            "confidence": 0.88,
            "hand_coords": {"x": 0.72, "y": 0.55}
        }
        self.handler.execute(
            gesture_result["gesture"],
            gesture_result["hand_coords"]
        )
        mock_move.assert_called_once()


if __name__ == "__main__":
    # Testleri verbosity=2 ile çalıştır — her test adı görünsün
    unittest.main(verbosity=2)
