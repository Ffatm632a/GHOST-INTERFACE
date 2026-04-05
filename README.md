# GHOST-INTERFAC

Bu proje, yapay zeka ve görüntü işleme tekniklerini kullanarak bilgisayar sistemlerini el hareketleriyle (temassız) kontrol etmeyi amaçlayan bir arayüz projesidir.

## 🚀 Proje Amacı
MediaPipe ve OpenCV kütüphanelerini kullanarak el landmark noktalarını tespit etmek ve bu noktaların birbirine göre konumlarından anlamlı "jestler" üreterek fare kontrolü, ses ayarı veya uygulama yönetimi sağlamak.

## 🛠 Kullanılan Teknolojiler
* **Python 3.10+**
* **OpenCV:** Kamera akışı ve görüntü işleme.
* **MediaPipe:** El tespiti ve landmark analizi.
* **Flask/FastAPI:** Web tabanlı kontrol paneli.

## 👥 Ekip ve Görev Dağılımı (Sprint 1)
* **Zeynep Karataş:** Kamera akışı ve el tespiti (`capture.py`, `hand_detector.py`)
* **Ceylin Güzelgörür:** Jest tanıma motoru (`gesture_engine.py`)
* **Dilara Bilişik:** Sistem entegrasyonu ve ayarlar (`command_handler.py`, `config.json`)
* **Elif Rümeysa Demir:** Web arayüzü geliştirme (`web_app.py`)
