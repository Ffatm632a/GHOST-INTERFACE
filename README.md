# Ghost Interface — Modül 3: Sistem Entegrasyonu & Komutlar

> **Sorumlu:** Üye 3 (Dilara)  
> **Branch:** `Dilara`  
> **Repo:** [GHOST-INTERFACE](https://github.com/Ffatm632a/GHOST-INTERFACE)

---

## Bu Modül Ne Yapar?

Jest tanıma motorundan (`gesture_engine.py`) gelen jest adlarını alır ve gerçek bilgisayar komutlarına dönüştürür.

```
gesture_engine.py → [jest adı + koordinat] → command_handler.py → [fare / ses / uygulama]
```

---

## Desteklenen Jestler

| Jest | Komut | Açıklama |
|------|-------|----------|
| `open_palm` | `mouse_move` | Fare imlecini el pozisyonuna taşır |
| `fist` | `left_click` | Sol fare tıklaması yapar |
| `thumb_up` | `volume_up` | Sistem sesini artırır |
| `thumb_down` | `volume_down` | Sistem sesini azaltır |
| `pinch_out` | `zoom_in` | Ekranı yakınlaştırır (Ctrl+) |
| `pinch_in` | `zoom_out` | Ekranı uzaklaştırır (Ctrl-) |
| `fist_open` | `open_app` | Config'deki uygulamayı açar |

---

## Kurulum

```bash
pip install -r requirements.txt
```

---

## Kullanım

```python
from command_handler import CommandHandler

handler = CommandHandler()

# Üye 2'den gelen veri
result = {
    "gesture": "thumb_up",
    "confidence": 0.95,
    "hand_coords": {"x": 0.45, "y": 0.30}
}

handler.execute(result["gesture"], result["hand_coords"])
```

---

## Testleri Çalıştır

```bash
python -m pytest tests/ -v
# veya
python -m unittest tests/test_command.py -v
```

---

## config.json Yapısı

```json
{
  "gestures": {
    "jest_adı": "komut_adı"
  },
  "app_to_open": "notepad",
  "volume_step": 5,
  "zoom_step": 0.1
}
```

> **Not:** Yeni jest eklemek için yalnızca `config.json` düzenlenir, kod değişikliği gerekmez.

---

## Platform Desteği

| Platform | Ses Kontrolü | Uygulama Açma |
|----------|-------------|---------------|
| Windows 10/11 | `keyboard.send("volume up/down")` | `subprocess.Popen(app, shell=True)` |
| Linux (Ubuntu 22.04) | `amixer -D pulse sset Master` | `subprocess.Popen([app])` |
| macOS | `osascript` | `subprocess.Popen(["open", "-a", app])` |

---

## Güvenlik Özellikleri

- **FAILSAFE:** Fare sol üst köşeye giderse PyAutoGUI otomatik durur
- **Graceful degradation:** Tanımsız jest gelirse sistem çökmez, log yazılır
- **Performans izleme:** 100ms eşiği aşılırsa uyarı logu üretilir
