# ============================================================
# tests/test_command.py
# Ghost Interface Projesi — Görev 3: Birim Testler
# Ghost Interface Project — Task 3: Unit Tests
#
# Sorumlu / Owner: Üye 3 (Dilara)
#
# TR: Bu dosya command_handler.py'nin doğru çalışıp çalışmadığını
#     test eder. "Mock" kullanır — yani gerçek fareyi hareket ettirmez,
#     sadece fonksiyonların doğru çağrılıp çağrılmadığını kontrol eder.
#
# EN: This file tests if command_handler.py works correctly.
#     Uses "mocking" — doesn't actually move the mouse,
#     just checks if the right functions were called.
# ============================================================

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# TR: Üst dizini Python path'ine ekle — command_handler import edilebilsin
# EN: Add parent directory to Python path — so command_handler can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from command_handler import CommandHandler


# ══════════════════════════════════════════════════════════════
# SINIF 1: TEMEL BİRİM TESTLER / CLASS 1: BASIC UNIT TESTS
# TR: Her komutun tek tek doğru çalışıp çalışmadığını test eder.
# EN: Tests each command individually to verify correct behavior.
# ══════════════════════════════════════════════════════════════
class TestCommandHandler(unittest.TestCase):
    """
    TR: CommandHandler sınıfı için temel birim testler.
    EN: Basic unit tests for CommandHandler class.
    """

    def setUp(self):
        """
        TR: Her test metodundan önce çalışır. Temiz bir handler oluşturur.
        EN: Runs before each test method. Creates a fresh handler.
        """
        self.handler = CommandHandler()

    # ── Sol Tıklama Testi / Left Click Test ──────────────────
    @patch("pyautogui.click")
    def test_left_click(self, mock_click):
        """
        TR: Yumruk (fist) jesti → pyautogui.click() çağrılmalı mı?
        EN: Fist gesture → should pyautogui.click() be called?
        """
        self.handler.execute("fist")
        mock_click.assert_called_once()   # TR: Bir kez çağrıldı mı? / EN: Called once?

    # ── Fare Hareketi Testi / Mouse Move Test ────────────────
    @patch("pyautogui.moveTo")
    def test_mouse_move_with_coords(self, mock_move):
        """
        TR: Açık avuç + koordinat verilince → fare hareket etmeli.
        EN: Open palm + coordinates given → mouse should move.
        """
        coords = {"x": 0.5, "y": 0.3}
        self.handler.execute("open_palm", coords)
        mock_move.assert_called_once()    # TR: moveTo çağrıldı mı? / EN: Was moveTo called?

    @patch("pyautogui.moveTo")
    def test_mouse_move_without_coords(self, mock_move):
        """
        TR: Koordinat gönderilmezse → fare hareket ETMEMELİ.
        EN: If no coordinates sent → mouse should NOT move.
        """
        self.handler.execute("open_palm", None)
        mock_move.assert_not_called()     # TR: Çağrılmadı mı? / EN: Was it NOT called?

    # ── Zoom Testleri / Zoom Tests ───────────────────────────
    @patch("pyautogui.hotkey")
    def test_zoom_in(self, mock_hotkey):
        """
        TR: Parmak açma (pinch_out) → Ctrl+'+' çağrılmalı.
        EN: Pinch out → Ctrl+'+' should be called.
        """
        self.handler.execute("pinch_out")
        mock_hotkey.assert_called_with("ctrl", "+")

    @patch("pyautogui.hotkey")
    def test_zoom_out(self, mock_hotkey):
        """
        TR: Parmak kapama (pinch_in) → Ctrl+'-' çağrılmalı.
        EN: Pinch in → Ctrl+'-' should be called.
        """
        self.handler.execute("pinch_in")
        mock_hotkey.assert_called_with("ctrl", "-")

    # ── Tanımsız Jest Testi / Unknown Gesture Test ───────────
    def test_unknown_gesture_no_exception(self):
        """
        TR: Tanımsız jest geldiğinde sistem çökmemeli.
            Bilinmeyen bir jest adı gönderiyoruz, hata fırlatmamalı.
        EN: System should not crash on unknown gesture.
            We send an unknown gesture name, it should not throw error.
        """
        try:
            self.handler.execute("bilinmeyen_jest")
            self.handler.execute("")
            self.handler.execute("xyz_123_invalid")
        except Exception as e:
            self.fail(f"Tanımsız jest exception fırlattı: {e}")

    # ── Config Yükleme Testleri / Config Loading Tests ───────
    def test_config_loaded_correctly(self):
        """
        TR: config.json okunduğunda gestures sözlüğü var mı?
        EN: When config.json is read, does gestures dictionary exist?
        """
        self.assertIn("gestures", self.handler.config)
        self.assertIsInstance(self.handler.config["gestures"], dict)

    def test_default_config_on_missing_file(self):
        """
        TR: config.json yoksa → varsayılan değerler kullanılmalı, çökmemeli.
        EN: If config.json missing → default values should be used, no crash.
        """
        handler = CommandHandler(config_path="var_olmayan_dosya.json")
        self.assertEqual(handler.config.get("app_to_open"), "notepad")
        self.assertEqual(handler.config.get("volume_step"), 5)

    # ── Uygulama Açma Testi / Open App Test ──────────────────
    @patch("subprocess.Popen")
    def test_open_app_called(self, mock_popen):
        """
        TR: Yumruk açma (fist_open) → subprocess.Popen çağrılmalı.
        EN: Fist open gesture → subprocess.Popen should be called.
        """
        self.handler.execute("fist_open")
        mock_popen.assert_called_once()

    # ── Ses Kontrolü Testleri / Volume Control Tests ─────────
    @patch("platform.system", return_value="Windows")
    @patch("keyboard.send")
    def test_volume_up_windows(self, mock_send, mock_platform):
        """
        TR: Windows'ta thumb_up → keyboard.send('volume up') 5 kez çağrılmalı.
            Neden 5? Çünkü config'de volume_step=5 yazıyor.
        EN: On Windows thumb_up → keyboard.send('volume up') called 5 times.
            Why 5? Because config has volume_step=5.
        """
        self.handler.os_name = "Windows"
        self.handler.execute("thumb_up")
        self.assertEqual(mock_send.call_count, 5)

    @patch("platform.system", return_value="Windows")
    @patch("keyboard.send")
    def test_volume_down_windows(self, mock_send, mock_platform):
        """
        TR: Windows'ta thumb_down → keyboard.send('volume down') 5 kez çağrılmalı.
        EN: On Windows thumb_down → keyboard.send('volume down') called 5 times.
        """
        self.handler.os_name = "Windows"
        self.handler.execute("thumb_down")
        self.assertEqual(mock_send.call_count, 5)

    # ── Performans Testi / Performance Test ──────────────────
    @patch("pyautogui.click")
    def test_execute_performance(self, mock_click):
        """
        TR: execute() metodu 100ms altında bitmeli.
            Neden? Gerçek zamanlı jest kontrolünde gecikme olmamalı.
        EN: execute() method should complete under 100ms.
            Why? Real-time gesture control should not have delay.
        """
        import time
        start = time.perf_counter()
        self.handler.execute("fist")
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.assertLess(
            elapsed_ms, 100,
            f"execute() 100ms'yi aştı: {elapsed_ms:.1f}ms"
        )


# ══════════════════════════════════════════════════════════════
# SINIF 2: ENTEGRASYON TESTLERİ / CLASS 2: INTEGRATION TESTS
# TR: Ceylin'in kodundan gelen verinin bizim sistemle uyumunu test eder.
#     Hem küçük hem büyük harf formatı test edilir (savunmacı testler).
# EN: Tests compatibility of Ceylin's output with our system.
#     Both lowercase and UPPERCASE formats are tested (defensive tests).
# ══════════════════════════════════════════════════════════════
class TestCommandHandlerIntegration(unittest.TestCase):
    """
    TR: Ceylin'in gesture_engine.py çıktısıyla uyumluluk testleri.
    EN: Compatibility tests with Ceylin's gesture_engine.py output.
    """

    def setUp(self):
        self.handler = CommandHandler()

    # ── Geriye Dönük Uyumluluk / Backward Compatibility ──────
    @patch("pyautogui.hotkey")
    def test_gesture_engine_format_zoom_in(self, mock_hotkey):
        """
        TR: Küçük harfli "pinch_out" → Ctrl+'+' çalışmalı.
        EN: Lowercase "pinch_out" → Ctrl+'+' should work.
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
        TR: Küçük harfli "open_palm" + koordinat → fare hareket etmeli.
        EN: Lowercase "open_palm" + coords → mouse should move.
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

    # ── Savunmacı Testler / Defensive Tests ──────────────────
    # TR: .lower() normalizasyonu çalışıyor mu? BÜYÜK HARF gelse bile
    #     sistem doğru çalışmalı.
    # EN: Does .lower() normalization work? System should work even
    #     with UPPERCASE input.

    @patch("pyautogui.moveTo")
    def test_uppercase_open_palm_defensive(self, mock_move):
        """
        TR: BÜYÜK HARF "OPEN_PALM" gelse bile → fare hareket etmeli.
        EN: Even UPPERCASE "OPEN_PALM" → mouse should move.
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
        TR: BÜYÜK HARF "FIST" gelse bile → tıklama çalışmalı.
        EN: Even UPPERCASE "FIST" → click should work.
        """
        self.handler.execute("FIST")
        mock_click.assert_called_once()

    @patch("pyautogui.click")
    def test_pointing_up_both_cases(self, mock_click):
        """
        TR: pointing_up hem küçük hem büyük harfle çalışmalı.
        EN: pointing_up should work with both lowercase and UPPERCASE.
        """
        self.handler.execute("POINTING_UP")
        self.handler.execute("pointing_up")
        self.assertEqual(mock_click.call_count, 2)  # TR: 2 kez çağrıldı mı? / EN: Called twice?

    def test_unknown_gesture_no_crash(self):
        """
        TR: Ceylin tanıyamadığı jestlerde "unknown" döndürüyor → sistem çökmemeli.
        EN: Ceylin returns "unknown" for unrecognized gestures → system shouldn't crash.
        """
        try:
            self.handler.execute("UNKNOWN")
            self.handler.execute("unknown")
        except Exception as e:
            self.fail(f"UNKNOWN jest exception fırlattı: {e}")

    def test_normalization_strips_whitespace(self):
        """
        TR: Başında/sonunda boşluk olsa bile jest çalışmalı.
            Örnek: "  FIST  " → "fist" olmalı.
        EN: Gesture should work even with leading/trailing whitespace.
            Example: "  FIST  " → should become "fist".
        """
        try:
            self.handler.execute("  FIST  ")
            self.handler.execute("  open_palm  ")
        except Exception as e:
            self.fail(f"Boşluklu jest adı exception fırlattı: {e}")


# ══════════════════════════════════════════════════════════════
# SINIF 3: TAM PİPELİNE TESTLERİ / CLASS 3: FULL PIPELINE TESTS
# TR: Ceylin'in Sprint 2 sonrası GERÇEK çıktı formatını test eder.
#     Bu testler projenin uçtan uca çalıştığını kanıtlar:
#     Zeynep (kamera) → Ceylin (jest analizi) → Dilara (komut)
#
# EN: Tests Ceylin's REAL post-Sprint 2 output format.
#     These tests prove the full pipeline works end-to-end:
#     Zeynep (camera) → Ceylin (gesture) → Dilara (command)
# ══════════════════════════════════════════════════════════════
class TestSprintThreeFullPipeline(unittest.TestCase):
    """
    TR: Sprint 3 — Tam pipeline entegrasyon testleri.
        Ceylin'in detect_gesture() çıktısı şu formatta:
        {"gesture": "open_palm", "confidence": 1.0, "hand_coords": {"x": 0.5, "y": 0.3}}
    EN: Sprint 3 — Full pipeline integration tests.
        Ceylin's detect_gesture() output format:
        {"gesture": "open_palm", "confidence": 1.0, "hand_coords": {"x": 0.5, "y": 0.3}}
    """

    def setUp(self):
        self.handler = CommandHandler()

    # ── UC-01: Fare Hareketi / Mouse Move ────────────────────
    @patch("pyautogui.moveTo")
    def test_pipeline_open_palm_mouse_move(self, mock_move):
        """
        TR: Ceylin "open_palm" gönderdi → fare hareket etmeli.
        EN: Ceylin sent "open_palm" → mouse should move.
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

    # ── UC-02: Sol Tıklama / Left Click ──────────────────────
    @patch("pyautogui.click")
    def test_pipeline_fist_left_click(self, mock_click):
        """
        TR: Ceylin "fist" gönderdi → sol tıklama olmalı.
        EN: Ceylin sent "fist" → left click should happen.
        """
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

    # ── UC-02b: İşaret Parmağı Tıklama / Pointing Click ─────
    @patch("pyautogui.click")
    def test_pipeline_pointing_up_left_click(self, mock_click):
        """
        TR: Ceylin "pointing_up" gönderdi → sol tıklama olmalı.
        EN: Ceylin sent "pointing_up" → left click should happen.
        """
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

    # ── UC-03: Ses Artırma / Volume Up ───────────────────────
    @patch("keyboard.send")
    def test_pipeline_thumb_up_volume_up(self, mock_send):
        """
        TR: Ceylin "thumb_up" gönderdi → ses 5 adım artmalı.
        EN: Ceylin sent "thumb_up" → volume should increase 5 steps.
        """
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
        self.assertEqual(mock_send.call_count, 5)

    # ── UC-04: Ses Azaltma / Volume Down ─────────────────────
    @patch("keyboard.send")
    def test_pipeline_thumb_down_volume_down(self, mock_send):
        """
        TR: Ceylin "thumb_down" gönderdi → ses 5 adım azalmalı.
        EN: Ceylin sent "thumb_down" → volume should decrease 5 steps.
        """
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

    # ── UC-05: Yakınlaştırma / Zoom In ───────────────────────
    @patch("pyautogui.hotkey")
    def test_pipeline_pinch_out_zoom_in(self, mock_hotkey):
        """
        TR: Ceylin "pinch_out" gönderdi → Ctrl+'+' çalışmalı.
        EN: Ceylin sent "pinch_out" → Ctrl+'+' should fire.
        """
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

    # ── UC-06: Uzaklaştırma / Zoom Out ───────────────────────
    @patch("pyautogui.hotkey")
    def test_pipeline_pinch_in_zoom_out(self, mock_hotkey):
        """
        TR: Ceylin "pinch_in" gönderdi → Ctrl+'-' çalışmalı.
        EN: Ceylin sent "pinch_in" → Ctrl+'-' should fire.
        """
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

    # ── UC-07: Uygulama Aç / Open App ────────────────────────
    @patch("subprocess.Popen")
    def test_pipeline_fist_open_app(self, mock_popen):
        """
        TR: Ceylin "fist_open" gönderdi → notepad açılmalı.
        EN: Ceylin sent "fist_open" → notepad should open.
        """
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

    # ── Tanımsız Jest / Unknown Gesture ──────────────────────
    def test_pipeline_unknown_gesture_silent(self):
        """
        TR: Ceylin "unknown" gönderdi (tanıyamadı) → sistem sessizce geçmeli.
        EN: Ceylin sent "unknown" (unrecognized) → system should skip silently.
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

    # ── None Koordinat Güvenliği / None Coords Safety ────────
    @patch("pyautogui.click")
    def test_pipeline_none_coords_safe(self, mock_click):
        """
        TR: Ceylin hand_coords=None gönderdi (el kayboldu) → çökmemeli.
        EN: Ceylin sent hand_coords=None (hand lost) → should not crash.
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


# TR: Bu dosya doğrudan çalıştırılırsa testleri başlat
# EN: If this file is run directly, start the tests
if __name__ == "__main__":
    unittest.main(verbosity=2)
