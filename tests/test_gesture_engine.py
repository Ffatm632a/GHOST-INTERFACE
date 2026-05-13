"""
gesture_engine.py icin birim testler — hata tespiti amacli
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock
from gesture_engine import GestureEngine

def make_landmarks(positions):
    """
    positions: list of (x, y) tuples, 21 adet olmali (landmark 0..20)
    """
    lms = []
    for x, y in positions:
        m = MagicMock()
        m.x = x
        m.y = y
        lms.append(m)
    return lms

# 21 landmark icin varsayilan template (hepsi 0.5, 0.5)
DEFAULT = [(0.5, 0.5)] * 21

def lm(overrides: dict):
    """overrides: {index: (x, y)}"""
    pts = list(DEFAULT)
    for idx, val in overrides.items():
        pts[idx] = val
    return make_landmarks(pts)


class TestGestureEngine(unittest.TestCase):

    def setUp(self):
        self.engine = GestureEngine()

    # --- Bos landmark ---
    def test_empty_landmarks_returns_unknown(self):
        result = self.engine.detect_gesture([])
        self.assertEqual(result["gesture"], "unknown")
        self.assertIsNone(result["hand_coords"])

    # --- thumb_up: sadece bas parmak kaldirilmis ---
    def test_thumb_up_detected(self):
        # landmark 4 (bas parmak ucu) landmark 3'ten sola (x daha kucuk) VE
        # landmark 4.y < landmark 5.y (yukarda)
        pts = list(DEFAULT)
        pts[3] = (0.6, 0.5)   # 3 sagda
        pts[4] = (0.3, 0.2)   # 4 solda ve yukarda => bas parmak kaldirilmis
        pts[5] = (0.5, 0.5)   # isaret parmagi tabanı
        # Diger parmaklar kapali: tip.y > pip.y
        for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
            pts[tip] = (0.5, 0.8)
            pts[pip] = (0.5, 0.5)
        result = self.engine.detect_gesture(make_landmarks(pts))
        self.assertEqual(result["gesture"], "thumb_up")

    # --- fist: tum parmaklar kapali ---
    def test_fist_detected(self):
        pts = list(DEFAULT)
        pts[3] = (0.4, 0.5); pts[4] = (0.6, 0.5)  # bas parmak kapali (4.x > 3.x)
        for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
            pts[tip] = (0.5, 0.8)
            pts[pip] = (0.5, 0.5)
        result = self.engine.detect_gesture(make_landmarks(pts))
        self.assertEqual(result["gesture"], "fist")

    # --- open_palm: tum parmaklar acik ---
    def test_open_palm_detected(self):
        pts = list(DEFAULT)
        pts[3] = (0.6, 0.5); pts[4] = (0.3, 0.5)  # bas parmak acik
        for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
            pts[tip] = (0.5, 0.2)
            pts[pip] = (0.5, 0.5)
        result = self.engine.detect_gesture(make_landmarks(pts))
        self.assertIn(result["gesture"], ["open_palm", "swipe_right", "swipe_left"])

    # --- pinch_in: mesafe < 0.06 ---
    def test_pinch_in_detected(self):
        pts = list(DEFAULT)
        pts[4] = (0.5, 0.5)
        pts[8] = (0.52, 0.5)  # mesafe ~0.02, threshold 0.06 altinda
        result = self.engine.detect_gesture(make_landmarks(pts))
        self.assertEqual(result["gesture"], "pinch_in")

    # --- swipe_right: 10 kare boyunca x artar ---
    def test_swipe_right_detected_after_window(self):
        engine = GestureEngine()
        pts = list(DEFAULT)
        # Tum parmaklar acik
        pts[3] = (0.6, 0.5); pts[4] = (0.3, 0.5)
        for tip, pip in [(8,6),(12,10),(16,14),(20,18)]:
            pts[tip] = (0.5, 0.2)
            pts[pip] = (0.5, 0.5)

        result = None
        # Landmark 0 x'ini her karede artir
        for i in range(10):
            pts[0] = (0.1 + i * 0.04, 0.5)  # toplam delta = 0.36 > 0.08
            result = engine.detect_gesture(make_landmarks(pts))
        self.assertEqual(result["gesture"], "swipe_right",
            f"Beklenen swipe_right, gelen: {result['gesture']}")

    # --- fist_open: gesture_engine'de TANIMSIZ ---
    def test_fist_open_never_produced(self):
        """
        BUG: gesture_engine hicbir zaman 'fist_open' uretmiyor.
        Bu test bu eksikligi belgeler.
        """
        possible = set()
        engine = GestureEngine()
        # Tum temel jest senaryolarini dene
        scenarios = [
            # fist
            {3:(0.4,0.5),4:(0.6,0.5),8:(0.5,0.8),6:(0.5,0.5),
             12:(0.5,0.8),10:(0.5,0.5),16:(0.5,0.8),14:(0.5,0.5),
             20:(0.5,0.8),18:(0.5,0.5)},
        ]
        for overrides in scenarios:
            pts = list(DEFAULT)
            for idx, val in overrides.items(): pts[idx] = val
            r = engine.detect_gesture(make_landmarks(pts))
            possible.add(r["gesture"])

        self.assertNotIn("fist_open", possible,
            "fist_open gesture_engine tarafindan URETILMEMELIDIR (zaten uretmiyor — bu BUG raporu)")

    # --- hand_coords None olmamali tanimli jestlerde ---
    def test_hand_coords_not_none_when_gesture_detected(self):
        pts = list(DEFAULT)
        pts[4] = (0.5, 0.5)
        pts[8] = (0.52, 0.5)
        result = self.engine.detect_gesture(make_landmarks(pts))
        if result["gesture"] != "unknown":
            self.assertIsNotNone(result["hand_coords"])

    # --- smoothing: gecmis temizleniyor mu ---
    def test_history_cleared_on_empty_landmarks(self):
        engine = GestureEngine()
        engine.history_x = [0.1, 0.2, 0.3]
        engine.history_y = [0.1, 0.2, 0.3]
        engine.detect_gesture([])
        self.assertEqual(engine.history_x, [])
        self.assertEqual(engine.history_y, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
