# 👻 GHOST-INTERFACE

Bu proje, yapay zeka ve görüntü işleme tekniklerini kullanarak bilgisayar sistemlerini el hareketleriyle (temassız) kontrol etmeyi amaçlayan bir arayüz projesidir.

## 🚀 Proje Amacı
MediaPipe ve OpenCV kütüphanelerini kullanarak el landmark noktalarını tespit etmek ve bu noktaların birbirine göre konumlarından anlamlı "jestler" üreterek fare kontrolü, ses ayarı veya uygulama yönetimi sağlamak.

---

## 👥 Ekip ve Görev Dağılımı
* **Zeynep Karataş (Üye 1):** Kamera akışı, el tespiti ve Web API entegrasyonu. (`hand_detector.py`, `camera_stream.py`)
* **Ceylin Güzelgörür (Üye 2):** Jest tanıma motoru, matematiksel analiz ve Hassasiyet Filtresi. (`gesture_engine.py`)
* **Dilara Bilişik (Üye 3):** Sistem entegrasyonu, komut yönetimi ve test süreçleri. (`command_handler.py`, `config.json`)
* **Elif Rümeysa Demir (Üye 4):** Web arayüzü ve kullanıcı paneli geliştirme. (`web_app.py`)

---

## 🛠 Kullanılan Teknolojiler
* **Python 3.10+**
* **OpenCV & MediaPipe:** Görüntü işleme ve el landmark analizi.
* **Flask:** Web tabanlı kontrol paneli ve canlı yayın.
* **PyAutoGUI & Keyboard:** Sistem seviyesi komut tetikleyicileri.

---

## ⚙️ Sistem Çalışma Mantığı

Sistem, modüler bir yapıda çalışarak el verilerini komuta dönüştürür:


### Desteklenen Jestler ve Komut Tablosu

| Jest | Komut | Açıklama |
|------|-------|----------|
| `open_palm` | `mouse_move` | Fare imlecini el pozisyonuna taşır |
| `fist` | `left_click` | Sol fare tıklaması yapar |
| `thumb_up` | `volume_up` | Sistem sesini artırır |
| `thumb_down` | `volume_down` | Sistem sesini azaltır |
| `pinch_out` | `zoom_in` | Ekranı yakınlaştırır (Ctrl+) |
| `pinch_in` | `zoom_out` | Ekranı uzaklaştırır (Ctrl-) |
| `fist_open` | `open_app` | Tanımlı uygulamayı (Notepad vb.) açar |

---

## 💻 Teknik Detaylar (Modül 3)

### config.json Yapısı
Yeni jestler eklemek için kod değişikliği gerekmez, yalnızca yapılandırma dosyası düzenlenir:
```json
{
  "gestures": { "jest_adı": "komut_adı" },
  "app_to_open": "notepad",
  "volume_step": 5,
  "zoom_step": 0.1
}




### 💻 Platform Desteği

Projemiz, farklı işletim sistemlerinde yerel komutları tetikleyebilecek şekilde optimize edilmiştir:

| Platform | Ses Kontrol Mekanizması | Uygulama Başlatma |
|----------|-------------------------|-------------------|
| **Windows 10/11** | `keyboard.send("volume up/down")` | `subprocess.Popen(shell=True)` |
| **Linux (Ubuntu)** | `amixer -D pulse sset Master` | `subprocess.Popen([app])` |
| **macOS** | `osascript -e "set volume..."` | `subprocess.Popen(["open", "-a", app])` |

> **Bilgi:** Sistem, çalıştığı işletim sistemini otomatik olarak tespit eder ve uygun sürücüyü (driver) devreye sokar.