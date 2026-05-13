document.addEventListener('DOMContentLoaded', () => {
    const fileInput       = document.getElementById('file-input');
    const welcomeScreen   = document.getElementById('welcome-screen');
    const mainDashboard   = document.getElementById('main-dashboard');
    const documentFrame   = document.getElementById('document-frame');
    const detectedGestureH3 = document.getElementById('detected-gesture');
    const gestureTextSpan = document.getElementById('gesture-text');
    const startBtn        = document.getElementById('start-btn');
    const resetBtn        = document.getElementById('reset-btn');
    const guideBtn        = document.getElementById('guide-btn');
    const guideModal      = document.getElementById('guide-modal');
    const closeGuideBtn   = document.getElementById('close-guide-btn');
    const langToggle      = document.getElementById('lang-toggle');
    const guideGridContainer = document.getElementById('guide-grid-container');

    let selectedFile = null;
    let currentLang  = 'tr';

    const gestures = [
        { id: "thumb_up",   icon: "👍", protocol: "[VOLUME_UP]",   tr: "Ses Aç",        en: "Volume Up"   },
        { id: "thumb_down", icon: "👎", protocol: "[VOLUME_DOWN]", tr: "Ses Kıs",        en: "Volume Down" },
        { id: "pinch_out",  icon: "🤌", protocol: "[ZOOM_IN]",     tr: "Yakınlaştır",    en: "Zoom In"     },
        { id: "pinch_in",   icon: "🤌", protocol: "[ZOOM_OUT]",    tr: "Uzaklaştır",     en: "Zoom Out"    },
        { id: "fist",       icon: "✊", protocol: "[CLICK]",       tr: "Tıkla",          en: "Click"       },
        { id: "swipe_right", icon: "👉", protocol: "[NEXT_PAGE]",   tr: "Sonraki Sayfa",  en: "Next Page"   },
        { id: "swipe_left",  icon: "👈", protocol: "[PREV_PAGE]",   tr: "Önceki Sayfa",   en: "Previous Page"}, 
        { id: "open_palm",  icon: "✋", protocol: "[MOUSE_MOVE]",  tr: "Fare Hareket",   en: "Mouse Move"  },
    ];

    const dict = {
        tr: { welcomeTitle:"GHOST INTERFACE", welcomeDesc:"Lütfen sisteme yüklemek veya görüntülemek için bir dosya seçin.", guideBtn:"Rehberi Görüntüle", startBtn:"Sistemi Başlat", resetBtn:"GERİ DÖN", chooseFile:"Dosya Seç", guideTitle:"Sistem Rehberi", closeGuideBtn:"Kapat", filesTitle:"Dosyalar", docTitle:"Döküman", streamTitle:"Canlı Akış", gestureTitle:"Son Jest", waiting:"SİNYAL BEKLENİYOR...", logsTitle:"Loglar", logInit:"Sistem başlatıldı.", logFileSelected:"Dosya seçildi: ", logSystemStarted:"Sistem başlatıldı.", logSystemClosed:"Sistem kapatıldı.", latency:"GECİKME:", fps:"FPS:", sysActive:"AKTİF", langBtn:"EN", viewing:"GÖRÜNTÜLENİYOR" },
        en: { welcomeTitle:"GHOST INTERFACE", welcomeDesc:"Please select a file to upload or view in the system.", guideBtn:"View Guide", startBtn:"Start System", resetBtn:"GO BACK", chooseFile:"Choose File", guideTitle:"System Guide", closeGuideBtn:"Close", filesTitle:"Files", docTitle:"Document", streamTitle:"Live Stream", gestureTitle:"Last Gesture", waiting:"WAITING FOR SIGNAL...", logsTitle:"Logs", logInit:"System initialized.", logFileSelected:"File selected: ", logSystemStarted:"System started.", logSystemClosed:"System shut down.", latency:"LATENCY:", fps:"FPS:", sysActive:"ACTIVE", langBtn:"TR", viewing:"VIEWING" }
    };

    function renderGuideGrid() {
        guideGridContainer.innerHTML = gestures.map(g => `
            <div class="guide-item">
                <div class="gesture-placeholder">${g.icon}</div>
                <div class="gesture-info">
                    <strong>${g.id}</strong>
                    <span>${g[currentLang]}</span>
                    <span class="protocol-name">${g.protocol}</span>
                </div>
            </div>`).join('');
    }

    function updateLanguage() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[currentLang][key]) el.innerText = dict[currentLang][key];
        });
        renderGuideGrid();
    }

    langToggle.addEventListener('click', () => {
        currentLang = currentLang === 'tr' ? 'en' : 'tr';
        updateLanguage();
    });

    guideBtn.addEventListener('click', () => guideModal.classList.remove('hidden'));
    closeGuideBtn.addEventListener('click', () => guideModal.classList.add('hidden'));

    fileInput.addEventListener('change', (e) => {
        selectedFile = e.target.files[0];
        startBtn.disabled = !selectedFile;
        if (selectedFile) addSystemLog(dict[currentLang].logFileSelected + selectedFile.name);
    });

    startBtn.addEventListener('click', () => {
        if (!selectedFile) return;
        welcomeScreen.classList.add('hidden');
        langToggle.classList.add('hidden');
        mainDashboard.classList.remove('hidden');
        addSystemLog(dict[currentLang].logSystemStarted);
        documentFrame.src = URL.createObjectURL(selectedFile) + "#toolbar=0&navpanes=0&scrollbar=0&view=Fit";
        document.getElementById('file-list').innerHTML = `
            <li class="file-item">
                <span>${selectedFile.name}</span>
                <span class="viewing-badge">${dict[currentLang].viewing}</span>
            </li>`;

        // Video feed'i ekle
        const vc = document.getElementById('video-container');
        if (!vc.querySelector('img')) {
            const img = document.createElement('img');
            img.src = '/video_feed';
            img.alt = 'Kamera';
            img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:8px;';
            vc.appendChild(img);
        }
    });

    resetBtn.addEventListener('click', () => {
        mainDashboard.classList.add('hidden');
        welcomeScreen.classList.remove('hidden');
        langToggle.classList.remove('hidden');
        selectedFile = null;
        fileInput.value = "";
        startBtn.disabled = true;
        documentFrame.src = "";
        document.getElementById('file-list').innerHTML = "";
        addSystemLog(dict[currentLang].logSystemClosed);
        const vc = document.getElementById('video-container');
        const img = vc.querySelector('img');
        if (img) {
            img.src = "";
            vc.removeChild(img);
        }
    });

    window.triggerGestureFeedback = function(gestureName) {
        detectedGestureH3.classList.replace('pulse-text', 'shake-active');
        gestureTextSpan.innerText = gestureName.toUpperCase();
        addSystemLog('Jest: ' + gestureName);
        documentFrame.classList.add('gesture-glow');
        setTimeout(() => {
            documentFrame.classList.remove('gesture-glow');
            detectedGestureH3.classList.replace('shake-active', 'pulse-text');
            gestureTextSpan.innerText = dict[currentLang].waiting;
        }, 1000);
    };

    function addSystemLog(message) {
        const logList = document.getElementById('system-logs');
        const timeString = new Date().toLocaleTimeString();
        const li = document.createElement('li');
        li.innerHTML = `<strong>[${timeString}]</strong> ${message}`;
        logList.prepend(li);
    }

    // FPS / Latency simülasyonu
    setInterval(() => {
        const le = document.getElementById('chip-latency');
        const fe = document.getElementById('chip-fps');
        if (le) le.innerText = Math.floor(Math.random() * 21 + 35) + "ms";
        if (fe) fe.innerText = Math.floor(Math.random() * 3 + 58);
    }, 1500);

    // ── Gesture Polling (Flask API) ──
    let lastGesture = "";
    setInterval(async () => {
        if (mainDashboard.classList.contains('hidden')) return;
        try {
            const r = await fetch('/api/status');
            const d = await r.json();
            const g = d.gesture;
            if (g && g !== "unknown" && g !== lastGesture) {
                lastGesture = g;
                window.triggerGestureFeedback(g);
            }
            if (g === "unknown") lastGesture = "";
        } catch(e) {}
    }, 500);

    // ── Particle field ──
    (function initParticles() {
        const canvas = document.getElementById('welcome-particles');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let particles = [];
        const COUNT = 70;
        function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
        resize();
        window.addEventListener('resize', resize);
        function rand(min, max) { return Math.random() * (max - min) + min; }
        function createParticle() { return { x: rand(0, canvas.width), y: rand(0, canvas.height), r: rand(0.8, 2.4), vx: rand(-0.25, 0.25), vy: rand(-0.4, -0.1), alpha: rand(0.3, 0.9), color: Math.random() > 0.5 ? '139,92,246' : '34,211,238' }; }
        for (let i = 0; i < COUNT; i++) particles.push(createParticle());
        function drawLines() {
            for (let i = 0; i < particles.length; i++) for (let j = i+1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x, dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 110) { ctx.beginPath(); ctx.strokeStyle = `rgba(139,92,246,${(1-dist/110)*0.12})`; ctx.lineWidth = 0.5; ctx.moveTo(particles[i].x, particles[i].y); ctx.lineTo(particles[j].x, particles[j].y); ctx.stroke(); }
            }
        }
        function tick() {
            if (welcomeScreen.classList.contains('hidden')) { requestAnimationFrame(tick); return; }
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawLines();
            particles.forEach(p => {
                ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
                ctx.fillStyle = `rgba(${p.color},${p.alpha})`; ctx.fill();
                p.x += p.vx; p.y += p.vy;
                if (p.y < -5) p.y = canvas.height + 5;
                if (p.x < -5) p.x = canvas.width + 5;
                if (p.x > canvas.width+5) p.x = -5;
            });
            requestAnimationFrame(tick);
        }
        tick();
    })();

    updateLanguage();
});
