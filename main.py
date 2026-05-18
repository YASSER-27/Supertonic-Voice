import sys, os, json, subprocess, uuid, wave, struct, math, time, shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from fast_autocomplete import AutoComplete # Fully integrated high-performance autocomplete engine!

# ── Robust BD Path Resolution ──
if getattr(sys, 'frozen', False):
    # Search executable parent directory first
    BD = Path(sys.executable).parent
    if not (BD / "tts_worker.exe").exists():
        # Fallback to current working directory
        BD = Path(os.getcwd())
        if not (BD / "tts_worker.exe").exists():
            # Fallback to PyInstaller temp resources folder
            BD = Path(sys._MEIPASS)
else:
    BD = Path(__file__).parent

# ── User Writable App Data / Output Directory Resolution ──
user_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "SupertonicVoice"
user_dir.mkdir(parents=True, exist_ok=True)

# ── Color Palette ──
ACCENT  = "#FF5A5F"
ACCENT2 = "#D9485A"

BG  = "#0F0F10"
BG2 = "#17181A"
BG3 = "#202225"

TXT  = "#F5F5F5"
TXT2 = "#8B8D93"

# ── Bilingual Vocabulary Dictionary ──
words = {
    # English vocabulary
    "hello": {}, "welcome": {}, "supertonic": {}, "voice": {}, "message": {},
    "generation": {}, "synthesizer": {}, "audio": {}, "karaoke": {}, "highlight": {},
    "playback": {}, "download": {}, "save": {}, "chrome": {}, "extension": {},
    "github": {}, "yasser-27": {}, "developer": {}, "interface": {}, "beautiful": {},
    "premium": {}, "offline": {}, "fast": {}, "speed": {}, "quality": {},
    "clear": {}, "sound": {}, "volume": {}, "speech": {}, "text": {},
    "translation": {}, "server": {}, "active": {}, "setup": {}, "installer": {},
    "project": {}, "folder": {}, "loop": {}, "typewriter": {}, "animate": {},
    "chat": {}, "input": {}, "button": {}, "waveform": {}, "visualizer": {},
    "you": {}, "your": {}, "yours": {}, "yourself": {}, "this": {},
    "that": {}, "these": {}, "those": {}, "what": {}, "when": {},
    "where": {}, "which": {}, "who": {}, "why": {}, "how": {},
    "want": {}, "will": {}, "work": {}, "please": {}, "thank": {},
    "thanks": {}, "perfect": {}, "again": {}, "retry": {}, "copy": {},
    "soundtrack": {}, "microphone": {}, "record": {}, "playback": {},
    
    # Arabic vocabulary (common words in conversations & text synthesis)
    "مرحبا": {}, "اهلا": {}, "صوت": {}, "رسالة": {}, "توليد": {},
    "تطبيق": {}, "تحميل": {}, "حفظ": {}, "جميل": {}, "سريع": {},
    "سرعة": {}, "جودة": {}, "واضح": {}, "نص": {}, "مشروع": {},
    "مساعد": {}, "تلقائي": {}, "موقع": {}, "شكرا": {}, "ممتاز": {},
    "شات": {}, "تعديل": {}, "قراءة": {}, "استماع": {}, "توقيف": {},
    "تشغيل": {}, "تكرار": {}, "تصحيح": {}, "كلمات": {}, "برنامج": {},
    "السلام": {}, "عليكم": {}, "رحمة": {}, "الله": {}, "وبركاته": {},
    "كيف": {}, "حالك": {}, "اليوم": {}, "معلومات": {}, "جديد": {},
    "تغيير": {}, "صوتي": {}, "الملف": {}, "تنزيل": {}, "نسخ": {},
    "تعديل": {}, "كتابة": {}, "رائع": {}, "سوبرتونيك": {}, "مطور": {}
}

class ApiServer(QThread):
    """Local light-weight HTTP server to securely and instantly receive requests from Chrome Extension"""
    request_received = Signal(str, str) # action, text

    def __init__(s, parent=None):
        super().__init__(parent)
        s.server = None

    def run(s):
        class ApiHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass # Suppress command line logging to keep output clean

            def do_OPTIONS(self):
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()

            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                try:
                    data = json.loads(post_data)
                    action = data.get("action")
                    text = data.get("text")
                    if action and text:
                        s.request_received.emit(action, text)
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                        return
                except Exception as e:
                    pass
                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

        try:
            s.server = HTTPServer(('127.0.0.1', 5003), ApiHandler)
            s.server.serve_forever()
        except Exception as e:
            print("API Server Error:", e)

    def stop(s):
        if s.server:
            s.server.shutdown()

class VectorButton(QPushButton):
    """Modern custom-drawn vector icon button with premium animations"""
    def __init__(s, btn_type, size=32, is_accent=False, parent=None):
        super().__init__(parent)
        s.type = btn_type
        s.setFixedSize(size, size)
        s.setCursor(Qt.PointingHandCursor)
        s.is_accent = is_accent
        s.hovered = False
        s.pressed = False

    def set_type(s, btn_type):
        s.type = btn_type
        s.update()

    def enterEvent(s, e):
        s.hovered = True
        s.update()

    def leaveEvent(s, e):
        s.hovered = False
        s.pressed = False
        s.update()

    def mousePressEvent(s, e):
        if e.button() == Qt.LeftButton:
            s.pressed = True
            s.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(s, e):
        s.pressed = False
        s.update()
        super().mouseReleaseEvent(e)

    def paintEvent(s, e):
        p = QPainter(s)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = s.width(), s.height()
        
        # Draw background circle
        bg_color = QColor(ACCENT) if s.is_accent else QColor("#2a2a2a")
        if s.hovered:
            bg_color = QColor(ACCENT2) if s.is_accent else QColor("#3a3a3a")
        if s.pressed:
            bg_color = QColor("#AA3333") if s.is_accent else QColor("#202020")
        
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bg_color))
        p.drawEllipse(0, 0, w, h)
        
        # Draw vector icon
        icon_color = QColor("#FFFFFF")
        p.setPen(QPen(icon_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        if s.type == "play":
            p.setBrush(QBrush(icon_color))
            path = QPainterPath()
            cx = w / 2
            cy = h / 2
            r = w * 0.18
            path.moveTo(cx - r * 0.6, cy - r)
            path.lineTo(cx + r * 1.1, cy)
            path.lineTo(cx - r * 0.6, cy + r)
            path.closeSubpath()
            p.drawPath(path)
        elif s.type == "pause":
            p.setBrush(QBrush(icon_color))
            bw = w * 0.08
            bh = h * 0.32
            cx = w / 2
            cy = h / 2
            p.drawRoundedRect(int(cx - bw * 1.8), int(cy - bh / 2), int(bw), int(bh), 1, 1)
            p.drawRoundedRect(int(cx + bw * 0.8), int(cy - bh / 2), int(bw), int(bh), 1, 1)
        elif s.type == "download":
            p.setBrush(Qt.NoBrush)
            cx = w / 2
            cy = h / 2
            r = w * 0.18
            p.drawLine(int(cx), int(cy - r), int(cx), int(cy + r * 0.5))
            p.drawLine(int(cx), int(cy + r * 0.5), int(cx - r * 0.6), int(cy - r * 0.1))
            p.drawLine(int(cx), int(cy + r * 0.5), int(cx + r * 0.6), int(cy - r * 0.1))
            p.drawLine(int(cx - r * 0.7), int(cy + r * 0.8), int(cx + r * 0.7), int(cy + r * 0.8))
        elif s.type == "stop":
            p.setBrush(QBrush(icon_color))
            r = w * 0.28
            p.drawRoundedRect(int((w - r) / 2), int((h - r) / 2), int(r), int(r), 1.5, 1.5)
        elif s.type == "copy":
            p.setBrush(Qt.NoBrush)
            cx = w / 2
            cy = h / 2
            r = w * 0.16
            p.drawRoundedRect(int(cx - r * 0.7), int(cy - r * 0.7), int(r * 1.1), int(r * 1.1), 1, 1)
            p.setBrush(QBrush(bg_color))
            p.drawRoundedRect(int(cx - r * 0.2), int(cy - r * 0.2), int(r * 1.1), int(r * 1.1), 1, 1)
        elif s.type == "retry":
            p.setBrush(Qt.NoBrush)
            cx = w / 2
            cy = h / 2
            r = w * 0.18
            rect = QRectF(cx - r, cy - r, r * 2, r * 2)
            p.drawArc(rect, 45 * 16, 270 * 16)
            path = QPainterPath()
            path.moveTo(cx + r, cy)
            path.lineTo(cx + r - 3, cy - 4)
            path.lineTo(cx + r + 3, cy - 4)
            path.closeSubpath()
            p.setBrush(QBrush(icon_color))
            p.drawPath(path)
        p.end()

class TTSWorker(QThread):
    """Background thread to run TTS conversion via tts_worker.exe"""
    finished = Signal(str, float)
    error = Signal(str)
    progress = Signal(int)

    def __init__(s, text, voice, parent=None):
        super().__init__(parent)
        s.text = text
        s.voice = voice

    def run(s):
        try:
            s.progress.emit(20)
            od = user_dir / "output"
            od.mkdir(exist_ok=True)
            op = str(od / f"v_{uuid.uuid4().hex[:8]}.wav")
            we = BD / "tts_worker.exe"
            md = str(BD)
            
            if we.exists():
                s.progress.emit(40)
                
                # PyInstaller environment isolation to prevent crosstalk in frozen state!
                env = os.environ.copy()
                env.pop("_MEIPASS", None)
                env.pop("PYTHONPATH", None)
                env.pop("PYTHONHOME", None)
                
                p = subprocess.Popen(
                    [str(we), "--model-dir", md],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(BD), # Force absolute working directory context
                    env=env, # Secure isolated environment variables
                    creationflags=0x08000000
                )
                r = json.loads(p.stdout.readline().decode('utf-8').strip())
                if "error" in r:
                    s.error.emit(r["error"])
                    return
                s.progress.emit(60)
                p.stdin.write((json.dumps({"text": s.text, "voice": s.voice, "output": op, "id": "1"}) + "\n").encode('utf-8'))
                p.stdin.flush()
                resp = json.loads(p.stdout.readline().decode('utf-8').strip())
                p.stdin.write((json.dumps({"action": "stop"}) + "\n").encode('utf-8'))
                p.stdin.flush()
                p.wait(timeout=5)
                if resp.get("success"):
                    s.progress.emit(100)
                    s.finished.emit(op, resp.get("duration", 0))
                else:
                    s.error.emit(resp.get("error", "Error generating audio"))
            else:
                # Fallback to local pyttsx3
                import pyttsx3
                e = pyttsx3.init()
                e.setProperty('rate', 160)
                e.save_to_file(s.text, op)
                e.runAndWait()
                s.progress.emit(100)
                with wave.open(op, 'r') as wf:
                    dur = wf.getnframes() / wf.getframerate()
                s.finished.emit(op, dur)
        except Exception as e:
            s.error.emit(str(e))

class WaveformWidget(QWidget):
    """Interactive voice message waveform visualizer"""
    def __init__(s, parent=None):
        super().__init__(parent)
        s.setFixedHeight(36)
        s.bars = [0.2] * 50
        s.pr = 0.0
        s.playing = False
        s._t = QTimer(s)
        s._t.timeout.connect(s.update)
        s._t.setInterval(80)

    def set_wav(s, path):
        try:
            with wave.open(path, 'r') as wf:
                n = wf.getnframes()
                fr = wf.readframes(n)
                sw = wf.getsampwidth()
                ch = wf.getnchannels()
                sa = struct.unpack(f'<{n*ch}h', fr) if sw == 2 else [0] * (n * ch)
                if ch > 1:
                    sa = sa[::ch]
                ck = max(1, len(sa) // 50)
                s.bars = []
                for i in range(50):
                    st = i * ck
                    en = min(st + ck, len(sa))
                    if st >= len(sa):
                        s.bars.append(0.1)
                        continue
                    s.bars.append(max(0.08, max(abs(x) for x in sa[st:en]) / 32768.0))
        except:
            s.bars = [0.2 + 0.3 * abs(math.sin(i * 0.3)) for i in range(50)]
        s.update()

    def set_progress(s, r):
        s.pr = max(0.0, min(1.0, r))
        s.update()

    def set_playing(s, p):
        s.playing = p
        if p:
            s._t.start()
        else:
            s._t.stop()
        s.update()

    def paintEvent(s, e):
        p = QPainter(s)
        p.setRenderHint(QPainter.Antialiasing)
        w = s.width()
        h = s.height()
        n = len(s.bars)
        bw = max(2, (w - n) / n)
        g = max(1, bw * 0.3)
        tw = n * (bw + g)
        off = (w - tw) / 2
        
        for i, v in enumerate(s.bars):
            x = off + i * (bw + g)
            r = i / max(1, n - 1)
            if s.playing and r <= s.pr:
                j = 0.05 * math.sin(time.time() * 8 + i * 0.5)
                bh = max(3, (v + j) * (h - 4))
            else:
                bh = max(3, v * (h - 4))
            y = (h - bh) / 2
            
            c = QColor(ACCENT) if r <= s.pr else QColor("#444")
            c.setAlpha(220 if r <= s.pr else 150)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(c))
            p.drawRoundedRect(int(x), int(y), int(bw), int(bh), 1.5, 1.5)
        p.end()

class UserBubble(QFrame):
    """User message chat bubble with Copy and Generate Again buttons placed perfectly on bottom-right"""
    def __init__(s, text, main_window, parent=None):
        super().__init__(parent)
        s.main_window = main_window
        s.text = text
        s.setStyleSheet(f"background:{ACCENT};border-radius:16px;border-bottom-right-radius:4px;")
        
        l = QVBoxLayout(s)
        l.setContentsMargins(14, 10, 14, 8)
        l.setSpacing(6)
        
        lb = QLabel(text)
        lb.setWordWrap(True)
        lb.setStyleSheet("color:white;font-size:13px;font-family:'Segoe UI';background:transparent;border:none;")
        lb.setTextInteractionFlags(Qt.TextSelectableByMouse)
        l.addWidget(lb)
        
        # Small toolbar at the bottom-right inside the bubble
        bot = QHBoxLayout()
        bot.setContentsMargins(0, 0, 0, 0)
        bot.setSpacing(6)
        bot.addStretch()
        
        # Retry/Generate Again button
        s.gen_btn = VectorButton("retry", 22)
        s.gen_btn.setToolTip("Generate Again / Change Voice")
        s.gen_btn.setStyleSheet("background:rgba(255,255,255,40);border-radius:11px;border:none;")
        s.gen_btn.clicked.connect(s._retry)
        bot.addWidget(s.gen_btn)
        
        # Copy button
        s.copy_btn = VectorButton("copy", 22)
        s.copy_btn.setToolTip("Copy Text")
        s.copy_btn.setStyleSheet("background:rgba(255,255,255,40);border-radius:11px;border:none;")
        s.copy_btn.clicked.connect(s._copy)
        bot.addWidget(s.copy_btn)
        
        l.addLayout(bot)

    def _copy(s):
        QApplication.clipboard().setText(s.text)
        QToolTip.showText(s.copy_btn.mapToGlobal(QPoint(0, -30)), "Copied!", s.copy_btn)

    def _retry(s):
        s.main_window.regenerate_voice(s.text)

class VoiceBubble(QFrame):
    """WhatsApp/Telegram style single chat bubble audio player (no wrapper boxes, no labels)"""
    def __init__(s, path, dur, parent=None):
        super().__init__(parent)
        s.ap = path
        s.td = dur
        s._playing = False
        s._seeking = False
        
        # Class-specific selector prevents stylesheet borders from cascading onto child widgets!
        s.setStyleSheet(f"VoiceBubble {{ background:{BG2};border-radius:16px;border-bottom-left-radius:4px;border:1px solid #2a2a2a; }} QLabel {{ border: none; }}")
        
        s.player = QMediaPlayer()
        s.ao = QAudioOutput()
        s.ao.setVolume(1.0)
        s.player.setAudioOutput(s.ao)
        s.player.setSource(QUrl.fromLocalFile(path))
        s.player.positionChanged.connect(s._pos)
        s.player.durationChanged.connect(s._dur)
        
        ml = QVBoxLayout(s)
        ml.setContentsMargins(12, 10, 12, 10)
        ml.setSpacing(6)
        
        top = QHBoxLayout()
        top.setSpacing(8)
        
        s.pb = VectorButton("play", 38, is_accent=True)
        s.pb.clicked.connect(s._toggle)
        top.addWidget(s.pb)
        
        s.wf = WaveformWidget()
        s.wf.set_wav(path)
        top.addWidget(s.wf, 1)
        
        s.sb = VectorButton("download", 32)
        s.sb.setToolTip("Save .wav")
        s.sb.clicked.connect(s._save)
        top.addWidget(s.sb)
        
        ml.addLayout(top)
        
        bot = QHBoxLayout()
        bot.setContentsMargins(4, 0, 4, 0)
        bot.setSpacing(6)
        
        s.tc = QLabel("0:00")
        s.tc.setStyleSheet(f"color:{TXT2};font-size:10px;font-family:Consolas;background:transparent;border:none;")
        s.tc.setFixedWidth(32)
        bot.addWidget(s.tc)
        
        s.sl = QSlider(Qt.Horizontal)
        s.sl.setRange(0, 1000)
        s.sl.setCursor(Qt.PointingHandCursor)
        s.sl.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: #333;
                height: 3px;
                border-radius: 1px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ACCENT};
                border-radius: 1px;
            }}
            QSlider::handle:horizontal {{
                background: {ACCENT};
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
                border: 2px solid {BG2};
            }}
        """)
        s.sl.sliderPressed.connect(lambda: setattr(s, '_seeking', True))
        s.sl.sliderReleased.connect(s._seek)
        s.sl.sliderMoved.connect(s._moved)
        bot.addWidget(s.sl, 1)
        
        s.tt = QLabel(s._f(dur))
        s.tt.setStyleSheet(f"color:{TXT2};font-size:10px;font-family:Consolas;background:transparent;border:none;")
        s.tt.setFixedWidth(32)
        s.tt.setAlignment(Qt.AlignRight)
        bot.addWidget(s.tt)
        
        ml.addLayout(bot)

    def _f(s, sec):
        m = int(max(0, sec)) // 60
        sc = int(max(0, sec)) % 60
        return f"{m}:{sc:02d}"

    def _toggle(s):
        if s._playing:
            s.player.pause()
            s.pb.set_type("play")
            s.wf.set_playing(False)
        else:
            s.player.play()
            s.pb.set_type("pause")
            s.wf.set_playing(True)
        s._playing = not s._playing

    def _pos(s, ms):
        if s.player.duration() > 0 and not s._seeking:
            r = ms / s.player.duration()
            s.sl.setValue(int(r * 1000))
            s.wf.set_progress(r)
            s.tc.setText(s._f(ms / 1000))
        if ms >= s.player.duration() > 0 and s._playing:
            s._playing = False
            s.pb.set_type("play")
            s.wf.set_playing(False)

    def _dur(s, ms):
        if ms > 0:
            s.td = ms / 1000
            s.tt.setText(s._f(s.td))

    def _seek(s):
        s._seeking = False
        if s.player.duration() > 0:
            s.player.setPosition(int(s.sl.value() / 1000 * s.player.duration()))

    def _moved(s, v):
        if s.player.duration() > 0:
            s.tc.setText(s._f(v / 1000 * s.player.duration() / 1000))
            s.wf.set_progress(v / 1000)

    def _save(s):
        p, _ = QFileDialog.getSaveFileName(s, "Save Voice", "", "WAV (*.wav)")
        if p:
            shutil.copy2(s.ap, p)

    def cleanup(s):
        s.player.stop()

class ReadBubble(QFrame):
    """Text message bubble with dynamic Karaoke highlighting and playback controls"""
    def __init__(s, text, parent=None):
        super().__init__(parent)
        s.full_text = text
        s.words = text.split()
        s._idx = -1
        s.audio_path = None
        s.duration = 0
        s.player = QMediaPlayer()
        s.ao = QAudioOutput()
        s.ao.setVolume(1.0)
        s.player.setAudioOutput(s.ao)
        
        # Explicit class-specific selector completely prevents borders from cascading onto label or time blocks!
        s.setStyleSheet(f"ReadBubble {{ background:{BG2};border-radius:16px;border-bottom-left-radius:4px;border:1px solid #2a2a2a; }} QLabel {{ border: none; }}")
        
        s.layout = QVBoxLayout(s)
        s.layout.setContentsMargins(14, 12, 14, 12)
        s.layout.setSpacing(8)
        
        s.label = QLabel(text)
        s.label.setWordWrap(True)
        s.label.setStyleSheet(f"color:{TXT};font-size:13px;font-family:'Segoe UI';background:transparent;border:none;line-height:1.5;")
        s.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        s.layout.addWidget(s.label)
        
        # Compact controller (initially hidden)
        s.ctrl = QWidget()
        s.ctrl.setStyleSheet("background:transparent;border:none;")
        cl = QHBoxLayout(s.ctrl)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)
        
        s.play_btn = VectorButton("pause", 28, is_accent=True)
        s.play_btn.clicked.connect(s._toggle_play)
        cl.addWidget(s.play_btn)
        
        s.stop_btn = VectorButton("stop", 28)
        s.stop_btn.clicked.connect(s.stop)
        cl.addWidget(s.stop_btn)
        
        s.time_lbl = QLabel("0:00 / 0:00")
        s.time_lbl.setStyleSheet(f"color:{TXT2};font-size:10px;font-family:Consolas;background:transparent;border:none;")
        cl.addWidget(s.time_lbl)
        cl.addStretch()
        
        s.layout.addWidget(s.ctrl)
        s.ctrl.hide()
        
        s.player.positionChanged.connect(s._pos_changed)
        s.player.playbackStateChanged.connect(s._state_changed)

    def set_audio(s, path, duration):
        s.audio_path = path
        s.duration = duration
        s.player.setSource(QUrl.fromLocalFile(path))
        s.ctrl.show()
        s.player.play()
        s.play_btn.set_type("pause")

    def _toggle_play(s):
        if s.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            s.player.pause()
            s.play_btn.set_type("play")
        else:
            s.player.play()
            s.play_btn.set_type("pause")

    def stop(s):
        s.player.stop()
        s.play_btn.set_type("play")
        s._idx = -1
        s.label.setText(s.full_text)
        s._update_time(0)

    def _state_changed(s, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            s.play_btn.set_type("play")
            s._idx = -1
            s.label.setText(s.full_text)
            s._update_time(0)

    def _pos_changed(s, ms):
        if s.player.duration() > 0:
            s._update_time(ms)
            r = ms / s.player.duration()
            total_words = len(s.words)
            idx = min(total_words - 1, int(r * total_words))
            if idx != s._idx and idx >= 0:
                s.highlight_word(idx)

    def _update_time(s, ms):
        cur = s._f(ms / 1000)
        tot = s._f(s.duration)
        s.time_lbl.setText(f"{cur} / {tot}")

    def _f(s, sec):
        m = int(max(0, sec)) // 60
        sc = int(max(0, sec)) % 60
        return f"{m}:{sc:02d}"

    def highlight_word(s, idx):
        s._idx = idx
        parts = []
        for i, w in enumerate(s.words):
            if i < idx:
                parts.append(f'<span style="color:#666;">{w}</span>')
            elif i == idx:
                parts.append(f'<span style="background:{ACCENT};color:white;border-radius:3px;padding:1px 3px;">{w}</span>')
            else:
                parts.append(f'<span style="color:{TXT};">{w}</span>')
        s.label.setText(" ".join(parts))

    def cleanup(s):
        s.player.stop()

class ChoiceBubble(QFrame):
    """Options bubble presented to the user after typing a message"""
    read_clicked = Signal()
    voice_clicked = Signal()

    def __init__(s, parent=None):
        super().__init__(parent)
        s.setStyleSheet("background:transparent;")
        l = QHBoxLayout(s)
        l.setContentsMargins(0, 4, 0, 4)
        l.setSpacing(8)
        
        for txt, sig, icon in [("📖 Read Here", s.read_clicked, "read"), ("🎙 Generate Voice", s.voice_clicked, "voice")]:
            b = QPushButton(txt)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(34)
            if icon == "read":
                b.setStyleSheet(f"""
                    QPushButton {{
                        background: {BG3};
                        color: {TXT};
                        border-radius: 12px;
                        font-size: 12px;
                        font-family: 'Segoe UI';
                        border: 1px solid #333;
                        padding: 0 16px;
                    }}
                    QPushButton:hover {{
                        background: #333;
                        border-color: {ACCENT};
                    }}
                """)
            else:
                b.setStyleSheet(f"""
                    QPushButton {{
                        background: {ACCENT};
                        color: white;
                        border-radius: 12px;
                        font-size: 12px;
                        font-weight: bold;
                        font-family: 'Segoe UI';
                        border: none;
                        padding: 0 16px;
                    }}
                    QPushButton:hover {{
                        background: {ACCENT2};
                    }}
                """)
            b.clicked.connect(sig.emit)
            l.addWidget(b)
        l.addStretch()

class TypewriterWelcome(QLabel):
    """Sleek single-line status message that types, pauses, backspaces, and loops through onboarding notices"""
    def __init__(s, parent=None):
        super().__init__(parent)
        s.setAlignment(Qt.AlignCenter)
        s.setStyleSheet(f"color:{ACCENT}; font-size:13px; font-weight:bold; font-family:'Segoe UI'; background:transparent; border:none;")
        
        s.lines = [
            "🎙️ Welcome to Supertonic Voice!",
            "❤️ Thank you for choosing Supertonic.",
            "💻 This app was created by yasser-27 on GitHub.",
            "⚠️ Note: Closing this app deletes all messages."
        ]
        s.line_idx = 0
        s.current_char = 0
        s.state = "TYPING" # "TYPING", "PAUSED", "CLEARING"
        
        s.timer = QTimer(s)
        s.timer.timeout.connect(s._tick)
        s.timer.setInterval(40) # Speed of typewriter

    def start_animation(s):
        s.line_idx = 0
        s.current_char = 0
        s.state = "TYPING"
        s.timer.start()

    def _tick(s):
        line = s.lines[s.line_idx]
        if s.state == "TYPING":
            if s.current_char < len(line):
                s.current_char += 1
                s.setText(line[:s.current_char])
            else:
                s.state = "PAUSED"
                s.timer.setInterval(2200) # Pause for 2.2 seconds on full message
        elif s.state == "PAUSED":
            s.state = "CLEARING"
            s.timer.setInterval(15) # Fast backspace clear speed
        elif s.state == "CLEARING":
            if s.current_char > 0:
                s.current_char -= 1
                s.setText(line[:s.current_char])
            else:
                s.state = "TYPING"
                s.line_idx = (s.line_idx + 1) % len(s.lines)
                s.timer.setInterval(40) # Reset to typing speed

class AutocompleteBar(QFrame):
    """Sleek, matching autocomplete suggestion chips bar placed directly above the input box"""
    suggestion_selected = Signal(str)

    def __init__(s, parent=None):
        super().__init__(parent)
        s.setFixedHeight(0) # Initially fully collapsed
        s.setStyleSheet("background:transparent; border:none;")
        
        s.layout = QHBoxLayout(s)
        s.layout.setContentsMargins(16, 2, 16, 2)
        s.layout.setSpacing(8)
        s.active_words = []

    def set_suggestions(s, words):
        # Clear out previous suggestion chips
        while s.layout.count():
            item = s.layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
                
        s.active_words = words
        if not words:
            s.setFixedHeight(0)
            return

        s.setFixedHeight(30)
        for w in words:
            btn = QPushButton(w)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG3};
                    color: {ACCENT};
                    border: 1px solid #333;
                    border-radius: 11px;
                    font-size: 11px;
                    font-family: 'Segoe UI';
                    padding: 2px 12px;
                }}
                QPushButton:hover {{
                    background: {ACCENT};
                    color: white;
                    border-color: {ACCENT};
                }}
            """)
            btn.clicked.connect(lambda checked=False, word=w: s.suggestion_selected.emit(word))
            s.layout.addWidget(btn)
        s.layout.addStretch()

class ChatInput(QTextEdit):
    """Chat input field that resizes automatically and supports Shift+Enter and Tab key autocomplete"""
    submit = Signal()

    def __init__(s, main_window, parent=None):
        super().__init__(parent)
        s.main_window = main_window
        s.setPlaceholderText("Type your message...")
        s.setAcceptRichText(False)
        s.setFixedHeight(40)
        s.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        s.document().contentsChanged.connect(s._resize)

    def _resize(s):
        h = min(120, max(40, int(s.document().size().height()) + 16))
        s.setFixedHeight(h)

    def keyPressEvent(s, e):
        if e.key() == Qt.Key_Tab:
            # Complete the word instantly if we have suggestions active!
            if s.main_window.ac_bar.active_words:
                e.accept()
                s.main_window.apply_completion(s.main_window.ac_bar.active_words[0])
                return
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.ShiftModifier):
            e.accept()
            s.submit.emit()
            return
        super().keyPressEvent(e)

class MainWindow(QMainWindow):
    def __init__(s):
        super().__init__()
        s.setWindowTitle("Supertonic Voice")
        s.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        s.setAttribute(Qt.WA_TranslucentBackground)
        s.setMinimumSize(440, 500)
        s.resize(460, 580)
        
        ic = BD / "icon.ico"
        if ic.exists():
            s.setWindowIcon(QIcon(str(ic)))
            s._icon_path = str(ic)
        else:
            s._icon_path = None
            
        s._drag = None
        s.voices = ["F1", "F2", "F3", "F4", "F5", "M1", "M2", "M3", "M4", "M5"]
        s.cur_voice = "F1"
        s.players = []
        s._threads = [] # Holds local worker threads to guarantee zero background crosstalk/overriding
        s.pending_text = None
        
        # Keep track of active layout chat bubble rows to guarantee perfect empty-state welcome checks!
        s.chat_bubbles = []
        
        # ── Setup bilingual high-performance fast-autocomplete ──
        english_chars = "abcdefghijklmnopqrstuvwxyz"
        arabic_chars = "".join(chr(c) for c in range(0x0600, 0x06FF))
        allowed_chars = frozenset(english_chars + arabic_chars + "0123456789 ")
        s.ac_engine = AutoComplete(words=words, valid_chars_for_string=allowed_chars)
        
        cw = QWidget()
        s.setCentralWidget(cw)
        root = QVBoxLayout(cw)
        root.setContentsMargins(10, 10, 10, 10)
        
        s.box = QFrame()
        s.box.setObjectName("box")
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(30)
        sh.setColor(QColor(0, 0, 0, 140))
        sh.setOffset(0, 4)
        s.box.setGraphicsEffect(sh)
        s.box.setStyleSheet(f"#box{{background:rgba(21, 21, 21, 220);border-radius:18px;border:1px solid #2a2a2a;}}")
        root.addWidget(s.box)
        
        ml = QVBoxLayout(s.box)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)
        
        # Title bar
        tb = QFrame()
        tb.setFixedHeight(48)
        tb.setStyleSheet("background:transparent;")
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(16, 0, 12, 0)
        tl.setSpacing(8)
        
        if s._icon_path:
            icl = QLabel()
            px = QPixmap(s._icon_path).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icl.setPixmap(px)
            icl.setStyleSheet("background:transparent;")
            tl.addWidget(icl)
            
        ttl = QLabel("Supertonic Voice")
        ttl.setStyleSheet(f"color:{ACCENT};font-size:14px;font-weight:bold;font-family:'Segoe UI';background:transparent;")
        tl.addWidget(ttl)
        tl.addStretch()
        
        for txt, slot, hc in [("─", s.showMinimized, "#3a3a3a"), ("✕", s.close, ACCENT)]:
            b = QPushButton(txt)
            b.setFixedSize(28, 28)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: #2a2a2a;
                    color: #888;
                    border-radius: 14px;
                    font-size: 12px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {hc};
                    color: white;
                }}
            """)
            b.clicked.connect(slot)
            tl.addWidget(b)
            
        ml.addWidget(tb)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#2a2a2a;")
        ml.addWidget(sep)
        
        # Chat area
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #333;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        s.chat_w = QWidget()
        s.chat_w.setStyleSheet("background:transparent;")
        s.chat_l = QVBoxLayout(s.chat_w)
        s.chat_l.setContentsMargins(16, 12, 16, 12)
        s.chat_l.setSpacing(10)
        
        # Looping status typewriter notice added perfectly at the center/bottom
        s.welcome = TypewriterWelcome()
        s.chat_l.addWidget(s.welcome)
        s.welcome.start_animation()
        
        s.chat_l.addStretch()
        sa.setWidget(s.chat_w)
        s.scroll = sa
        ml.addWidget(sa, 1)
        
        # Autocomplete bar matching layout placed directly above input frame
        s.ac_bar = AutocompleteBar()
        s.ac_bar.suggestion_selected.connect(s.apply_completion)
        ml.addWidget(s.ac_bar)
        
        # Input area
        inp_f = QFrame()
        inp_f.setStyleSheet(f"background:{BG2};border-top:1px solid #2a2a2a;border-bottom-left-radius:18px;border-bottom-right-radius:18px;")
        il = QHBoxLayout(inp_f)
        il.setContentsMargins(12, 10, 12, 10)
        il.setSpacing(8)
        
        s.vb = QPushButton("F1")
        s.vb.setFixedSize(38, 38)
        s.vb.setCursor(Qt.PointingHandCursor)
        s.vb.setStyleSheet(f"""
            QPushButton {{
                background: {BG3};
                color: {ACCENT};
                border-radius: 19px;
                font-size: 10px;
                font-weight: bold;
                font-family: 'Segoe UI';
                border: 1px solid #333;
            }}
            QPushButton:hover {{
                border-color: {ACCENT};
            }}
        """)
        s.vb.clicked.connect(s._show_voice_menu)
        il.addWidget(s.vb)
        
        s.inp = ChatInput(s)
        s.inp.setStyleSheet(f"""
            QTextEdit {{
                background: {BG3};
                color: {TXT};
                border: 1px solid #333;
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Segoe UI';
                selection-background-color: {ACCENT};
            }}
            QTextEdit:focus {{
                border-color: {ACCENT};
            }}
        """)
        s.inp.submit.connect(s._send)
        s.inp.textChanged.connect(s._on_input_changed)
        il.addWidget(s.inp, 1)
        
        s.send_btn = QPushButton("➤")
        s.send_btn.setFixedSize(38, 38)
        s.send_btn.setCursor(Qt.PointingHandCursor)
        s.send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT};
                color: white;
                border-radius: 19px;
                font-size: 16px;
                border: none;
            }}
            QPushButton:hover {{
                background: {ACCENT2};
            }}
        """)
        s.send_btn.clicked.connect(s._send)
        il.addWidget(s.send_btn)
        
        ml.addWidget(inp_f)
        
        # Progress bar
        s.prog = QProgressBar()
        s.prog.setRange(0, 100)
        s.prog.setFixedHeight(3)
        s.prog.setTextVisible(False)
        s.prog.setStyleSheet(f"QProgressBar{{background:transparent;border:none;}}QProgressBar::chunk{{background:{ACCENT};}}")
        s.prog.hide()
        ml.addWidget(s.prog)
        
        # Start API Server instantly
        s.api_server = ApiServer()
        s.api_server.request_received.connect(s._on_api_request)
        s.api_server.start()

    def _show_voice_menu(s):
        m = QMenu(s)
        m.setStyleSheet(f"""
            QMenu {{
                background: {BG3};
                color: {TXT};
                border: 1px solid #333;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background: {ACCENT};
                color: white;
            }}
        """)
        for v in s.voices:
            a = m.addAction(v)
            a.triggered.connect(lambda c, v=v: s._set_voice(v))
        m.exec(s.vb.mapToGlobal(QPoint(0, -m.sizeHint().height())))

    def _set_voice(s, v):
        s.cur_voice = v
        s.vb.setText(v)

    def _add_bubble(s, w, align="left"):
        # Explicit welcome hiding guarantees welcome bar stops and vanishes the moment chat starts!
        s.welcome.hide()
        s.welcome.timer.stop()
        
        s.chat_bubbles.append(w) # Securely track active chat bubble rows
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        if align == "right":
            row.addStretch()
            row.addWidget(w)
            w.setMaximumWidth(320)
        else:
            row.addWidget(w)
            row.addStretch()
            w.setMaximumWidth(360)
        s.chat_l.insertLayout(s.chat_l.count() - 1, row)
        QTimer.singleShot(50, lambda: s.scroll.verticalScrollBar().setValue(s.scroll.verticalScrollBar().maximum()))

    def _add_user_message(s, text):
        # Explicit welcome hiding guarantees welcome bar stops and vanishes the moment chat starts!
        s.welcome.hide()
        s.welcome.timer.stop()
        
        ub = UserBubble(text, s)
        s.chat_bubbles.append(ub) # Securely track user bubble rows
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch()
        row.addWidget(ub)
        ub.setMaximumWidth(320)
        s.chat_l.insertLayout(s.chat_l.count() - 1, row)
        QTimer.singleShot(50, lambda: s.scroll.verticalScrollBar().setValue(s.scroll.verticalScrollBar().maximum()))

    def _on_input_changed(s):
        """Monitors typing activity to hide welcome looping text instantly and update suggestion keywords"""
        val = s.inp.toPlainText()
        has_typed_content = bool(val.strip())
        
        # Welcoming notices looping rules (Only show welcome line when chat is completely empty and no text is written)
        if has_typed_content or len(s.chat_bubbles) > 0:
            s.welcome.hide()
            s.welcome.timer.stop()
        else:
            s.welcome.show()
            if not s.welcome.timer.isActive():
                s.welcome.start_animation()
                
        # Autocomplete search rules
        if not has_typed_content:
            s.ac_bar.set_suggestions([])
            return
            
        cursor = s.inp.textCursor()
        pos = cursor.position()
        
        # Grab current word context
        words_before_cursor = val[:pos].split()
        if not words_before_cursor:
            s.ac_bar.set_suggestions([])
            return
            
        typing_word = words_before_cursor[-1].lower()
        if len(typing_word) < 1:
            s.ac_bar.set_suggestions([])
            return
            
        # Match keywords using fast-autocomplete DWG engine (flattening results list of lists)
        results = s.ac_engine.search(typing_word, size=4)
        matches = [r[0] for r in results if r]
        s.ac_bar.set_suggestions(matches)

    def apply_completion(s, word):
        """Triggered automatically by Tab key or suggestion chip click to auto-complete"""
        cursor = s.inp.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(word + " ")
        s.ac_bar.set_suggestions([])
        s.inp.setFocus()

    def _send(s):
        t = s.inp.toPlainText().strip()
        if not t:
            return
        s.inp.clear()
        s._add_user_message(t)
        s.pending_text = t
        cb = ChoiceBubble()
        cb.read_clicked.connect(lambda: s._do_read(t, cb))
        cb.voice_clicked.connect(lambda: s._do_voice(t, cb))
        s._add_bubble(cb, "left")

    def regenerate_voice(s, text):
        """Triggered automatically by clicking 'Generate Again' toolbar button inside the UserBubble"""
        s.prog.show()
        s.prog.setValue(0)
        
        worker = TTSWorker(text, s.cur_voice)
        worker.progress.connect(s.prog.setValue)
        worker.finished.connect(lambda p, d: s._voice_done(p, d))
        worker.error.connect(s._voice_err)
        s._threads.append(worker)
        worker.finished.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.error.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.start()

    def _do_read(s, text, choice):
        choice.hide()
        rb = ReadBubble(text)
        s._add_bubble(rb, "left")
        s.players.append(rb)
        
        s.prog.show()
        s.prog.setValue(0)
        
        worker = TTSWorker(text, s.cur_voice)
        worker.progress.connect(s.prog.setValue)
        worker.finished.connect(lambda p, d, rb=rb: s._read_ready(rb, p, d))
        worker.error.connect(s._voice_err)
        s._threads.append(worker)
        worker.finished.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.error.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.start()

    def _read_ready(s, rb, path, dur):
        s.prog.hide()
        rb.set_audio(path, dur)

    def _do_voice(s, text, choice):
        choice.hide()
        s.prog.show()
        s.prog.setValue(0)
        
        worker = TTSWorker(text, s.cur_voice)
        worker.progress.connect(s.prog.setValue)
        worker.finished.connect(lambda p, d: s._voice_done(p, d))
        worker.error.connect(s._voice_err)
        s._threads.append(worker)
        worker.finished.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.error.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
        worker.start()

    def _voice_done(s, path, dur):
        s.prog.hide()
        vb = VoiceBubble(path, dur)
        s._add_bubble(vb, "left")
        s.players.append(vb)

    def _voice_err(s, err):
        s.prog.hide()
        el = QLabel(f"❌ {err}")
        el.setStyleSheet(f"color:{ACCENT};font-size:12px;padding:8px;")
        s._add_bubble(el, "left")

    def _on_api_request(s, action, text):
        """Called automatically when Chrome Extension triggers play/generate action"""
        s.show()
        s.raise_()
        s.activateWindow()
        
        s._add_user_message(text)
        
        if action == "voice":
            s.prog.show()
            s.prog.setValue(0)
            worker = TTSWorker(text, s.cur_voice)
            worker.progress.connect(s.prog.setValue)
            worker.finished.connect(lambda p, d: s._voice_done(p, d))
            worker.error.connect(s._voice_err)
            s._threads.append(worker)
            worker.finished.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
            worker.error.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
            worker.start()
        elif action == "read":
            rb = ReadBubble(text)
            s._add_bubble(rb, "left")
            s.players.append(rb)
            
            s.prog.show()
            s.prog.setValue(0)
            worker = TTSWorker(text, s.cur_voice)
            worker.progress.connect(s.prog.setValue)
            worker.finished.connect(lambda p, d, rb=rb: s._read_ready(rb, p, d))
            worker.error.connect(s._voice_err)
            s._threads.append(worker)
            worker.finished.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
            worker.error.connect(lambda: s._threads.remove(worker) if worker in s._threads else None)
            worker.start()

    def mousePressEvent(s, e):
        if e.button() == Qt.LeftButton and e.position().y() < 50:
            s._drag = e.globalPosition().toPoint() - s.frameGeometry().topLeft()

    def mouseMoveEvent(s, e):
        if s._drag and e.buttons() & Qt.LeftButton:
            s.move(e.globalPosition().toPoint() - s._drag)

    def mouseReleaseEvent(s, e):
        s._drag = None

    def closeEvent(s, e):
        s.api_server.stop()
        s.api_server.wait()
        for p in s.players:
            p.cleanup()
        e.accept()

def main():
    a = QApplication(sys.argv)
    a.setStyle("Fusion")
    ic = BD / "icon.ico"
    if ic.exists():
        a.setWindowIcon(QIcon(str(ic)))
    
    p = a.palette()
    p.setColor(p.ColorRole.Window, QColor(BG))
    p.setColor(p.ColorRole.WindowText, QColor(TXT))
    p.setColor(p.ColorRole.Base, QColor(BG3))
    p.setColor(p.ColorRole.Text, QColor(TXT))
    p.setColor(p.ColorRole.Highlight, QColor(ACCENT))
    a.setPalette(p)
    
    w = MainWindow()
    w.show()
    sys.exit(a.exec())

if __name__ == "__main__":
    main()
