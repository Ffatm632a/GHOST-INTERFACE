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
    Üye 2'nin (Ceylin) gesture_engine.py'sinden gelecek gerçek veri
    formatı simüle edilir.

    ── Versiyon Geçmişi ──────────────────────────────────────
    Sprint 2: Ceylin BÜYÜK HARF döndürüyordu → .lower() ile çözdük
    Sprint 3: Ceylin küçük harf + dictionary formatına geçti
              Eski testler geriye dönük uyumluluk için korundu
    """

    def setUp(self):
        """Her testten önce handler oluştur."""
        self.handler = CommandHandler()

    # ── Geriye Dönük Uyumluluk Testleri (küçük harf string) ──
    @patch("pyautogui.hotkey")
    def test_gesture_engine_format_zoom_in(self, mock_hotkey):
        """
        Küçük harfli jest adıyla zoom in testi (geriye dönük uyumluluk).
        """
        gesture_result = {
            "gesture": "pinch_out",
            "confidence": 0.95,
            "hand_coords": {"x": 0.45, "y": 0.30}
        }
        self.handler.execute(
            gesture_result["gesture"],
            gesture_result["hand_coords"]
        )
        mock_hotkey.assert_called_with("ctrl", "+")

    @patch("pyautogui.moveTo")
    def test_gesture_engine_format_mouse_move(self, mock_move):
        """
        Küçük harfli jest adıyla fare hareketi testi (geriye dönük uyumluluk).
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

    # ── BÜYÜK HARF Savunmacı Testler (.lower() katmanı) ─────
    # Ceylin artık küçük harf gönderiyor ama .lower() normalizasyonu
    # gelecekte format değişirse sistemi korur. Bu testler savunmacı
    # katmanın çalıştığını doğruluyor.

    @patch("pyautogui.moveTo")
    def test_uppercase_open_palm_defensive(self, mock_move):
        """
        Savunmacı Test: BÜYÜK HARF gelse bile .lower() ile çalışmalı.
        """
        gesture_result = {
            "gesture": "OPEN_PALM",
            "confidence": 0.92,
            "hand_coords": {"x": 0.5, "y": 0.4}
        }
        self.handler.execute(
            gesture_result["gesture"],
            gesture_result["hand_coords"]
        )
        mock_move.assert_called_once()

    @patch("pyautogui.click")
    def test_uppercase_fist_defensive(self, mock_click):
        """
        Savunmacı Test: BÜYÜK HARF 'FIST' gelse bile sol tıklama çalışmalı.
        """
        self.handler.execute("FIST")
        mock_click.assert_called_once()

    @patch("pyautogui.click")
    def test_pointing_up_both_cases(self, mock_click):
        """pointing_up hem küçük hem büyük harfle çalışmalı."""
        self.handler.execute("POINTING_UP")
        self.handler.execute("pointing_up")
        self.assertEqual(mock_click.call_count, 2)

    def test_unknown_gesture_no_crash(self):
        """
        Tanımsız jest geldiğinde sistem çökmemeli.
        Ceylin'in gesture_engine.py'si tanıyamadığı jestlerde 'unknown' döndürüyor.
        """
        try:
            self.handler.execute("UNKNOWN")
            self.handler.execute("unknown")
        except Exception as e:
            self.fail(f"UNKNOWN jest exception fırlattı: {e}")

    def test_normalization_strips_whitespace(self):
        """Başında/sonunda boşluk olan jest adları da doğru çalışmalı."""
        try:
            self.handler.execute("  FIST  ")
            self.handler.execute("  open_palm  ")
        except Exception as e:
            self.fail(f"Boşluklu jest adı exception fırlattı: {e}")


class TestSprintThreeFullPipeline(unittest.TestCase):
    """
    ════════════════════════════════════════════════════════════
    Sprint 3 — Tam Pipeline Entegrasyon Testleri
    ════════════════════════════════════════════════════════════
    Bu test sınıfı, Ceylin'in Sprint 2 sonrası gesture_engine.py'sinin
    GERÇEK çıktı formatını birebir simüle eder.

    Ceylin'in detect_gesture() artık şu formatı döndürüyor:
        {
            "gesture": "open_palm",        # küçük harf (str)
            "confidence": 1.0,             # float
            "hand_coords": {"x": 0.5, "y": 0.3}  # dict veya None
        }

    Zeynep'in hand_detector.py → Ceylin'in gesture_engine.py →
    Dilara'nın command_handler.py zinciri burada uçtan uca test ediliyor.
    """

    def setUp(self):
        """Her testten önce temiz handler."""
        self.handler = CommandHandler()

    # ── UC-01: Fare Hareketi (Açık Avuç) ─────────────────────
    @patch("pyautogui.moveTo")
    def test_pipeline_open_palm_mouse_move(self, mock_move):
        """
        Tam Pipeline: Ceylin 'open_palm' → handler → pyautogui.moveTo()
        Zeynep'in hand_detector'ından normalize koordinat geliyor.
        """
        ceylin_output = {
            "gesture": "open_palm",
            "confidence": 1.0,
            "hand_coords": {"x": 0.45, "y": 0.30}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_move.assert_called_once()

    # ── UC-02: Sol Tıklama (Yumruk) ──────────────────────────
    @patch("pyautogui.click")
    def test_pipeline_fist_left_click(self, mock_click):
        """Tam Pipeline: Ceylin 'fist' → handler → pyautogui.click()"""
        ceylin_output = {
            "gesture": "fist",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.5}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_click.assert_called_once()

    # ── UC-02b: Sol Tıklama (İşaret Parmağı) ─────────────────
    @patch("pyautogui.click")
    def test_pipeline_pointing_up_left_click(self, mock_click):
        """Tam Pipeline: Ceylin 'pointing_up' → handler → pyautogui.click()"""
        ceylin_output = {
            "gesture": "pointing_up",
            "confidence": 1.0,
            "hand_coords": {"x": 0.6, "y": 0.4}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_click.assert_called_once()

    # ── UC-03: Ses Artırma (Baş Parmak Yukarı) ───────────────
    @patch("keyboard.send")
    def test_pipeline_thumb_up_volume_up(self, mock_send):
        """Tam Pipeline: Ceylin 'thumb_up' → handler → keyboard.send('volume up')"""
        self.handler.os_name = "Windows"
        ceylin_output = {
            "gesture": "thumb_up",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.2}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        self.assertEqual(mock_send.call_count, 5)  # volume_step=5

    # ── UC-04: Ses Azaltma (Baş Parmak Aşağı) ────────────────
    @patch("keyboard.send")
    def test_pipeline_thumb_down_volume_down(self, mock_send):
        """Tam Pipeline: Ceylin 'thumb_down' → handler → keyboard.send('volume down')"""
        self.handler.os_name = "Windows"
        ceylin_output = {
            "gesture": "thumb_down",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.8}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        self.assertEqual(mock_send.call_count, 5)

    # ── UC-05: Zoom In (Parmak Açma) ─────────────────────────
    @patch("pyautogui.hotkey")
    def test_pipeline_pinch_out_zoom_in(self, mock_hotkey):
        """Tam Pipeline: Ceylin 'pinch_out' → handler → Ctrl+Plus"""
        ceylin_output = {
            "gesture": "pinch_out",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.5}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_hotkey.assert_called_with("ctrl", "+")

    # ── UC-06: Zoom Out (Parmak Kapama) ──────────────────────
    @patch("pyautogui.hotkey")
    def test_pipeline_pinch_in_zoom_out(self, mock_hotkey):
        """Tam Pipeline: Ceylin 'pinch_in' → handler → Ctrl+Minus"""
        ceylin_output = {
            "gesture": "pinch_in",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.5}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_hotkey.assert_called_with("ctrl", "-")

    # ── UC-07: Uygulama Aç (Yumruk Açma) ─────────────────────
    @patch("subprocess.Popen")
    def test_pipeline_fist_open_app(self, mock_popen):
        """Tam Pipeline: Ceylin 'fist_open' → handler → subprocess.Popen('notepad')"""
        ceylin_output = {
            "gesture": "fist_open",
            "confidence": 1.0,
            "hand_coords": {"x": 0.5, "y": 0.5}
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_popen.assert_called_once()

    # ── Tanımsız Jest (Sessiz Geçiş) ─────────────────────────
    def test_pipeline_unknown_gesture_silent(self):
        """
        Tam Pipeline: Ceylin tanıyamadığı jestlerde 'unknown' döndürür.
        Handler bu değeri config'de bulamaz, sessizce geçer.
        Sistem çökmez, hata vermez.
        """
        ceylin_output = {
            "gesture": "unknown",
            "confidence": 0.0,
            "hand_coords": None
        }
        try:
            self.handler.execute(
                ceylin_output["gesture"],
                ceylin_output["hand_coords"]
            )
        except Exception as e:
            self.fail(f"Pipeline 'unknown' jest ile çöktü: {e}")

    # ── None Koordinat Güvenliği ──────────────────────────────
    @patch("pyautogui.click")
    def test_pipeline_none_coords_safe(self, mock_click):
        """
        Ceylin bazen hand_coords=None gönderebilir (el kaybolduğunda).
        Sistem çökmemeli.
        """
        ceylin_output = {
            "gesture": "fist",
            "confidence": 1.0,
            "hand_coords": None
        }
        self.handler.execute(
            ceylin_output["gesture"],
            ceylin_output["hand_coords"]
        )
        mock_click.assert_called_once()


if __name__ == "__main__":
    # Testleri verbosity=2 ile çalıştır — her test adı görünsün
    unittest.main(verbosity=2)

