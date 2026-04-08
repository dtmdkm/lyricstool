import sys
import os
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QScrollArea, QFrame,
    QComboBox, QLineEdit, QTextEdit, QProgressBar, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont

# ── constants ────────────────────────────────────────────────────────────────

AUDIO_EXTS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac",
    ".wma", ".opus", ".mp4", ".mkv", ".avi", ".mov",
}

LANGUAGES = {
    "Tự động phát hiện": "auto",
    "Tiếng Việt": "vi",
    "English": "en",
    "日本語 (Japanese)": "ja",
    "한국어 (Korean)": "ko",
    "中文 (Chinese)": "zh",
    "Français": "fr",
    "Deutsch": "de",
    "Español": "es",
    "Italiano": "it",
    "Português": "pt",
    "Русский": "ru",
    "ภาษาไทย": "th",
}

MODELS = {
    "tiny  — Nhanh nhất  (~39 MB)":   "tiny",
    "base  — Nhanh       (~74 MB)":   "base",
    "small — Cân bằng   (~244 MB)":   "small",
    "medium — Chính xác (~769 MB)":   "medium",
    "large-v3 — Tốt nhất (~1.5 GB)": "large-v3",
}

# ── stylesheet ───────────────────────────────────────────────────────────────

APP_STYLE = """
QMainWindow, QWidget {
    background-color: #0d0d1f;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
    font-size: 13px;
}
QFrame#card {
    background-color: #13132b;
    border-radius: 12px;
}
QFrame#dropZone {
    border: 2px dashed #3d3d7a;
    border-radius: 16px;
    background-color: #11112a;
    min-height: 150px;
}
QFrame#dropZone:hover {
    border-color: #7c3aed;
    background-color: #1a1a3e;
}
QFrame#dropHover {
    border: 2px dashed #7c3aed;
    border-radius: 16px;
    background-color: #1e1b4b;
    min-height: 150px;
}
QLabel#title {
    color: #e2e8f0;
    font-size: 22px;
    font-weight: bold;
    background: transparent;
}
QLabel#subtitle {
    color: #64748b;
    font-size: 12px;
    background: transparent;
}
QLabel#section {
    color: #a78bfa;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    background: transparent;
}
QLabel#hint {
    color: #475569;
    font-size: 13px;
    background: transparent;
}
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c3aed, stop:1 #2563eb);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 32px;
    font-size: 15px;
    font-weight: bold;
    min-height: 46px;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #6d28d9, stop:1 #1d4ed8);
}
QPushButton#primary:disabled {
    background: #1e293b;
    color: #475569;
}
QPushButton#secondary {
    background-color: #1e293b;
    color: #94a3b8;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}
QPushButton#secondary:hover {
    background-color: #2d3748;
    color: #e2e8f0;
}
QPushButton#remove {
    background-color: transparent;
    color: #475569;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: bold;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}
QPushButton#remove:hover {
    background-color: #7f1d1d;
    color: #fca5a5;
}
QComboBox {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 6px 12px;
    min-width: 180px;
}
QComboBox QLineEdit {
    color: #e2e8f0;
    background-color: transparent;
    border: none;
    padding: 0px;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #2d3748;
    selection-background-color: #4c1d95;
    outline: none;
}
QLineEdit {
    background-color: #1e293b;
    color: #94a3b8;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 6px 12px;
}
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical {
    background: #0d0d1f;
    width: 5px;
    border-radius: 3px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3d3d7a;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTextEdit {
    background-color: #08081a;
    color: #6ee7b7;
    border: 1px solid #1e293b;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 8px;
}
QProgressBar {
    background-color: #1e293b;
    border: none;
    border-radius: 3px;
    height: 5px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7c3aed, stop:1 #2563eb);
    border-radius: 3px;
}
"""

# ── DropZone widget ──────────────────────────────────────────────────────────

class DropZone(QFrame):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        icon = QLabel("🎵")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 44px; background: transparent; border: none;")

        main_txt = QLabel("Kéo & thả nhiều file âm thanh vào đây")
        main_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_txt.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #a78bfa; background: transparent; border: none;"
        )

        fmt_txt = QLabel("MP3 · WAV · M4A · FLAC · OGG · AAC · WMA · OPUS")
        fmt_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fmt_txt.setStyleSheet("font-size: 11px; color: #475569; background: transparent; border: none;")

        or_txt = QLabel("hoặc")
        or_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_txt.setStyleSheet("font-size: 11px; color: #334155; background: transparent; border: none;")

        browse_btn = QPushButton("📂  Chọn file...")
        browse_btn.setObjectName("secondary")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse)

        layout.addWidget(icon)
        layout.addWidget(main_txt)
        layout.addWidget(fmt_txt)
        layout.addWidget(or_txt)
        layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _browse(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn file âm thanh", "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma *.opus "
            "*.mp4 *.mkv *.avi *.mov);;All Files (*)",
        )
        if files:
            self.files_dropped.emit(files)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.setObjectName("dropHover")
            self.setStyleSheet(APP_STYLE)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setObjectName("dropZone")
        self.setStyleSheet(APP_STYLE)

    def dropEvent(self, event: QDropEvent):
        self.setObjectName("dropZone")
        self.setStyleSheet(APP_STYLE)
        files = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if Path(url.toLocalFile()).suffix.lower() in AUDIO_EXTS
        ]
        if files:
            self.files_dropped.emit(files)
        event.acceptProposedAction()

# ── Per-file row widget ──────────────────────────────────────────────────────

class FileRow(QWidget):
    remove_clicked = pyqtSignal(str)

    PENDING    = "pending"
    PROCESSING = "processing"
    DONE       = "done"
    ERROR      = "error"

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path
        self.status = self.PENDING
        self._build()

    def _build(self):
        self.setStyleSheet(
            "QWidget { background-color: #13132b; border-radius: 8px; }"
        )
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(10)

        self.icon_lbl = QLabel("⏳")
        self.icon_lbl.setFixedWidth(22)
        self.icon_lbl.setStyleSheet("background: transparent; font-size: 14px;")

        info = QVBoxLayout()
        info.setSpacing(2)

        name = Path(self.path).name
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet(
            "background: transparent; color: #e2e8f0; font-size: 13px; font-weight: 500;"
        )
        self.name_lbl.setToolTip(self.path)

        self.size_lbl = QLabel(self._file_size())
        self.size_lbl.setStyleSheet("background: transparent; color: #475569; font-size: 11px;")

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setFixedHeight(4)
        self.prog_bar.hide()

        self.status_lbl = QLabel()
        self.status_lbl.setStyleSheet("background: transparent; color: #64748b; font-size: 11px;")
        self.status_lbl.hide()

        info.addWidget(self.name_lbl)
        info.addWidget(self.size_lbl)
        info.addWidget(self.prog_bar)
        info.addWidget(self.status_lbl)

        self.remove_btn = QPushButton("✕")
        self.remove_btn.setObjectName("remove")
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.path))

        root.addWidget(self.icon_lbl)
        root.addLayout(info, 1)
        root.addWidget(self.remove_btn)

    def _file_size(self) -> str:
        try:
            b = os.path.getsize(self.path)
            if b < 1024:       return f"{b} B"
            if b < 1024**2:    return f"{b/1024:.1f} KB"
            return f"{b/1024**2:.1f} MB"
        except Exception:
            return ""

    # ── state helpers ────────────────────────────────────────────────────────

    def mark_processing(self):
        self.status = self.PROCESSING
        self.icon_lbl.setText("🔄")
        self.prog_bar.setValue(0)
        self.prog_bar.show()
        self.status_lbl.setText("Đang xử lý...")
        self.status_lbl.setStyleSheet("background: transparent; color: #a78bfa; font-size: 11px;")
        self.status_lbl.show()
        self.remove_btn.hide()

    def update_progress(self, pct: int, text: str = ""):
        self.prog_bar.setValue(pct)
        if text:
            self.status_lbl.setText(text)

    def mark_done(self, out_path: str):
        self.status = self.DONE
        self.icon_lbl.setText("✅")
        self.prog_bar.setValue(100)
        self.status_lbl.setText(f"✓ Đã lưu: {Path(out_path).name}")
        self.status_lbl.setStyleSheet("background: transparent; color: #6ee7b7; font-size: 11px;")
        self.remove_btn.show()

    def mark_error(self, msg: str):
        self.status = self.ERROR
        self.icon_lbl.setText("❌")
        self.prog_bar.hide()
        self.status_lbl.setText(f"Lỗi: {msg[:60]}")
        self.status_lbl.setStyleSheet("background: transparent; color: #f87171; font-size: 11px;")
        self.remove_btn.show()

    def reset_pending(self):
        self.status = self.PENDING
        self.icon_lbl.setText("⏳")
        self.prog_bar.setValue(0)
        self.prog_bar.hide()
        self.status_lbl.hide()
        self.remove_btn.show()

# ── Worker thread ────────────────────────────────────────────────────────────

class Worker(QThread):
    sig_progress = pyqtSignal(str, int, str)  # path, pct, text
    sig_done     = pyqtSignal(str, str)        # path, out_path
    sig_error    = pyqtSignal(str, str)        # path, msg
    sig_log      = pyqtSignal(str)
    sig_finished = pyqtSignal()

    def __init__(self, files: list[str], out_dir: str, language: str, model: str):
        super().__init__()
        self.files    = files
        self.out_dir  = out_dir
        self.language = language
        self.model    = model
        self._stop    = False

    def cancel(self):
        self._stop = True

    def run(self):
        from core.audio_processor import convert_to_wav
        from core.transcriber    import transcribe_audio
        from core.srt_generator  import save_srt

        self._log(f"Bắt đầu xử lý {len(self.files)} file(s)")
        self._log(f"Model: {self.model}  |  Ngôn ngữ: {self.language or 'auto'}")

        for path in self.files:
            if self._stop:
                self._log("⚠ Đã hủy")
                break
            self._process(path, convert_to_wav, transcribe_audio, save_srt)

        self.sig_finished.emit()

    def _process(self, path, convert_to_wav, transcribe_audio, save_srt):
        name = Path(path).name
        tmp_wav = None
        try:
            self._log(f"▶ {name}")
            self.sig_progress.emit(path, 8, "Chuẩn hóa audio (FFmpeg)...")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_wav = f.name
            convert_to_wav(path, tmp_wav)

            # status will be updated by status_callback once model is ready
            lang = None if self.language == "auto" else self.language

            import time
            _t0 = [time.time()]

            def on_prog(cur, total):
                elapsed = int(time.time() - _t0[0])
                pct = min(90, int(22 + (cur / total) * 68))
                self.sig_progress.emit(
                    path, pct,
                    f"Nhận dạng... {cur:.0f}s / {total:.0f}s  ({elapsed}s đã qua)"
                )

            def on_status(pct, text):
                self.sig_progress.emit(path, pct, text)

            segments, detected = transcribe_audio(
                tmp_wav,
                language=lang,
                model_size=self.model,
                progress_callback=on_prog,
                log_callback=self._log,
                status_callback=on_status,
            )

            self._log(f"  → Ngôn ngữ: {detected}  |  {len(segments)} đoạn")
            self.sig_progress.emit(path, 93, "Xuất file SRT...")

            stem = Path(path).stem
            out_path = os.path.join(self.out_dir, f"{stem}.srt")
            counter = 1
            while os.path.exists(out_path):
                out_path = os.path.join(self.out_dir, f"{stem}_{counter}.srt")
                counter += 1

            save_srt(segments, out_path)
            self.sig_progress.emit(path, 100, "Hoàn thành!")
            self.sig_done.emit(path, out_path)
            self._log(f"  ✓ Đã lưu: {Path(out_path).name}")

        except Exception as exc:
            self.sig_error.emit(path, str(exc))
            self._log(f"  ✗ Lỗi: {exc}")
        finally:
            if tmp_wav:
                try:
                    os.unlink(tmp_wav)
                except Exception:
                    pass

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.sig_log.emit(f"[{ts}] {msg}")

# ── Main window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._rows: dict[str, FileRow] = {}
        self._worker: Worker | None = None
        self._build_ui()
        self.setStyleSheet(APP_STYLE)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("🎵  Lyrics to SRT Converter")
        self.setMinimumSize(740, 720)
        self.resize(800, 780)

        root = QWidget()
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(24, 20, 24, 20)
        vbox.setSpacing(14)

        # ── header ──────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title_col = QVBoxLayout()
        t = QLabel("🎵 Lyrics to SRT Converter")
        t.setObjectName("title")
        sub = QLabel("Chuyển đổi file âm thanh thành phụ đề SRT cho CapCut, Premiere, DaVinci...")
        sub.setObjectName("subtitle")
        title_col.addWidget(t)
        title_col.addWidget(sub)
        hdr.addLayout(title_col)
        hdr.addStretch()
        vbox.addLayout(hdr)

        # ── drop zone ────────────────────────────────────────────────────────
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._add_files)
        vbox.addWidget(self.drop_zone)

        # ── file list header ─────────────────────────────────────────────────
        fh = QHBoxLayout()
        self.count_lbl = QLabel("FILES (0)")
        self.count_lbl.setObjectName("section")
        add_btn = QPushButton("+ Thêm file")
        add_btn.setObjectName("secondary")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._browse_add)
        self.clear_btn = QPushButton("Xóa tất cả")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self._clear_all)
        fh.addWidget(self.count_lbl)
        fh.addStretch()
        fh.addWidget(add_btn)
        fh.addWidget(self.clear_btn)
        vbox.addLayout(fh)

        # ── scrollable file list ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(160)
        scroll.setMaximumHeight(270)
        scroll.setStyleSheet(
            "QScrollArea { border: 1px solid #1e293b; border-radius: 10px; "
            "background-color: #0d0d1f; }"
        )

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(8, 8, 8, 8)
        self.list_layout.setSpacing(6)

        self.empty_lbl = QLabel("Chưa có file nào. Kéo thả hoặc nhấn vào vùng trên để thêm.")
        self.empty_lbl.setObjectName("hint")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "QLabel { padding: 30px; color: #334155; font-size: 13px; }"
        )
        self.list_layout.addWidget(self.empty_lbl)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_widget)
        vbox.addWidget(scroll)

        # ── settings card ────────────────────────────────────────────────────
        sec_lbl = QLabel("CÀI ĐẶT")
        sec_lbl.setObjectName("section")
        vbox.addWidget(sec_lbl)

        card = QFrame()
        card.setObjectName("card")
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(16, 14, 16, 14)
        card_v.setSpacing(12)

        # language + model row
        lm_row = QHBoxLayout()
        lm_row.setSpacing(24)

        lang_col = QVBoxLayout()
        lang_col.setSpacing(4)
        ll = QLabel("Ngôn ngữ:")
        ll.setStyleSheet("background: transparent; color: #94a3b8; font-size: 12px;")
        self.lang_cb = QComboBox()
        for k, v in LANGUAGES.items():
            self.lang_cb.addItem(k, v)
        lang_col.addWidget(ll)
        lang_col.addWidget(self.lang_cb)

        model_col = QVBoxLayout()
        model_col.setSpacing(4)
        ml = QLabel("Model Whisper:")
        ml.setStyleSheet("background: transparent; color: #94a3b8; font-size: 12px;")
        self.model_cb = QComboBox()
        for k, v in MODELS.items():
            self.model_cb.addItem(k, v)
        self.model_cb.setCurrentIndex(2)  # small by default
        model_col.addWidget(ml)
        model_col.addWidget(self.model_cb)

        lm_row.addLayout(lang_col)
        lm_row.addLayout(model_col)
        lm_row.addStretch()
        card_v.addLayout(lm_row)

        # output folder row
        out_row = QHBoxLayout()
        out_row.setSpacing(8)
        ol = QLabel("📁  Lưu vào:")
        ol.setStyleSheet("background: transparent; color: #94a3b8; font-size: 12px;")
        ol.setFixedWidth(72)

        default_out = str(Path.home() / "Downloads")
        self.out_edit = QLineEdit(default_out)
        self.out_edit.setReadOnly(True)

        out_browse = QPushButton("Chọn thư mục…")
        out_browse.setObjectName("secondary")
        out_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        out_browse.clicked.connect(self._pick_out_dir)

        out_row.addWidget(ol)
        out_row.addWidget(self.out_edit, 1)
        out_row.addWidget(out_browse)
        card_v.addLayout(out_row)

        vbox.addWidget(card)

        # ── start button ─────────────────────────────────────────────────────
        self.start_btn = QPushButton("🚀   Bắt đầu chuyển đổi")
        self.start_btn.setObjectName("primary")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._toggle_processing)
        vbox.addWidget(self.start_btn)

        # ── log section ──────────────────────────────────────────────────────
        log_hdr = QHBoxLayout()
        log_sec = QLabel("LOG")
        log_sec.setObjectName("section")
        self.open_dir_btn = QPushButton("📂  Mở thư mục xuất")
        self.open_dir_btn.setObjectName("secondary")
        self.open_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_dir_btn.clicked.connect(self._open_out_dir)
        log_hdr.addWidget(log_sec)
        log_hdr.addStretch()
        log_hdr.addWidget(self.open_dir_btn)
        vbox.addLayout(log_hdr)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(120)
        self.log_box.setPlaceholderText("Thông tin xử lý sẽ hiển thị ở đây…")
        vbox.addWidget(self.log_box)

    # ── file management ──────────────────────────────────────────────────────

    def _add_files(self, paths: list[str]):
        for p in paths:
            if p not in self._rows:
                row = FileRow(p)
                row.remove_clicked.connect(self._remove_file)
                # insert before the trailing stretch
                idx = self.list_layout.count() - 1
                self.list_layout.insertWidget(idx, row)
                self._rows[p] = row
        if self._rows:
            self.empty_lbl.hide()
        self._refresh_state()

    def _remove_file(self, path: str):
        if path in self._rows:
            w = self._rows.pop(path)
            self.list_layout.removeWidget(w)
            w.deleteLater()
        if not self._rows:
            self.empty_lbl.show()
        self._refresh_state()

    def _clear_all(self):
        for w in list(self._rows.values()):
            self.list_layout.removeWidget(w)
            w.deleteLater()
        self._rows.clear()
        self.empty_lbl.show()
        self._refresh_state()

    def _browse_add(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Chọn file âm thanh", "",
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.ogg *.aac "
            "*.wma *.opus *.mp4 *.mkv *.avi *.mov);;All Files (*)",
        )
        if files:
            self._add_files(files)

    def _refresh_state(self):
        n = len(self._rows)
        self.count_lbl.setText(f"FILES ({n})")
        self.start_btn.setEnabled(n > 0)
        self.clear_btn.setEnabled(n > 0)

    # ── processing ───────────────────────────────────────────────────────────

    def _toggle_processing(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self.start_btn.setText("🚀   Bắt đầu chuyển đổi")
            return

        pending = [
            p for p, r in self._rows.items()
            if r.status == FileRow.PENDING
        ]
        if not pending:
            # retry all files
            for row in self._rows.values():
                row.reset_pending()
            pending = list(self._rows.keys())

        out_dir = self.out_edit.text()
        os.makedirs(out_dir, exist_ok=True)

        language  = self.lang_cb.currentData()
        model_sz  = self.model_cb.currentData()

        self.log_box.clear()
        self.start_btn.setText("⏹   Hủy")

        for p in pending:
            self._rows[p].mark_processing()

        self._worker = Worker(pending, out_dir, language, model_sz)
        self._worker.sig_progress.connect(self._on_prog)
        self._worker.sig_done.connect(self._on_done)
        self._worker.sig_error.connect(self._on_error)
        self._worker.sig_log.connect(self._on_log)
        self._worker.sig_finished.connect(self._on_finished)
        self._worker.start()

    def _on_prog(self, path: str, pct: int, text: str):
        if path in self._rows:
            self._rows[path].update_progress(pct, text)

    def _on_done(self, path: str, out_path: str):
        if path in self._rows:
            self._rows[path].mark_done(out_path)

    def _on_error(self, path: str, msg: str):
        if path in self._rows:
            self._rows[path].mark_error(msg)

    def _on_log(self, msg: str):
        self.log_box.append(msg)
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_finished(self):
        self.start_btn.setText("🚀   Bắt đầu chuyển đổi")
        done = sum(1 for r in self._rows.values() if r.status == FileRow.DONE)
        total = len(self._rows)
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(
            f"[{ts}] ══════ Hoàn thành {done}/{total} file(s) ══════"
        )

    # ── helpers ──────────────────────────────────────────────────────────────

    def _pick_out_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Chọn thư mục lưu file SRT", self.out_edit.text()
        )
        if folder:
            self.out_edit.setText(folder)

    def _open_out_dir(self):
        d = self.out_edit.text()
        if not os.path.exists(d):
            return
        if sys.platform == "win32":
            os.startfile(d)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", d])
        else:
            subprocess.Popen(["xdg-open", d])


# ── entry point ──────────────────────────────────────────────────────────────

def _apply_dark_palette(app: QApplication) -> None:
    """Set dark QPalette so Fusion style renders text correctly in packaged exe."""
    from PyQt6.QtGui import QPalette, QColor
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window,          QColor(13,  13,  31))
    p.setColor(QPalette.ColorRole.WindowText,      QColor(226, 232, 240))
    p.setColor(QPalette.ColorRole.Base,            QColor(30,  41,  59))
    p.setColor(QPalette.ColorRole.AlternateBase,   QColor(19,  19,  43))
    p.setColor(QPalette.ColorRole.Text,            QColor(226, 232, 240))
    p.setColor(QPalette.ColorRole.Button,          QColor(30,  41,  59))
    p.setColor(QPalette.ColorRole.ButtonText,      QColor(226, 232, 240))
    p.setColor(QPalette.ColorRole.BrightText,      QColor(255, 255, 255))
    p.setColor(QPalette.ColorRole.Highlight,       QColor(76,  29,  149))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.ColorRole.ToolTipBase,     QColor(30,  41,  59))
    p.setColor(QPalette.ColorRole.ToolTipText,     QColor(226, 232, 240))
    p.setColor(QPalette.ColorRole.PlaceholderText, QColor(100, 116, 139))
    app.setPalette(p)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrics SRT Converter")
    app.setStyle("Fusion")
    _apply_dark_palette(app)   # fixes empty ComboBox text in packaged exe
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
