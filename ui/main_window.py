import sys
import os
import subprocess
import json
import shutil
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QCheckBox, QListWidget, 
    QPlainTextEdit, QProgressBar, QStackedWidget, QFileDialog, 
    QMessageBox, QLabel, QTabWidget, QSizeGrip, QApplication,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QThread, Signal, QPoint
from PySide6.QtGui import (
    QColor, QTextCharFormat, QFont, QTextCursor
)

# Importamos lógica (asegúrate de que existan en tu proyecto)
from engines.pyinstaller_engine import build_command as build_pyinstaller_command
from engines.obfuscation_engine import run_obfuscator
from ui.obfuscation_widget import ObfuscationWidget

# ==============================================================================
# 🎨 ESTILOS CSS
# ==============================================================================

STYLES_XENO = """
/* === TEMA XENO (Black & Minimal) === */
QMainWindow, QWidget#CentralWidget { background-color: #050505; }
QLabel { font-family: 'Segoe UI', sans-serif; color: #777777; font-size: 12px; font-weight: 500; }
QLabel#Header { color: #ffffff; font-size: 14px; font-weight: bold; letter-spacing: 0.5px; }
QFrame.Card { background-color: #0a0a0a; border: 1px solid #1f1f1f; border-radius: 8px; }
QLineEdit { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; padding: 10px; color: #ffffff; font-family: 'Consolas', monospace; font-size: 12px; }
QLineEdit:focus { border: 1px solid #555555; background-color: #080808; }
QListWidget { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; color: #cccccc; outline: none; }
QCheckBox { color: #999999; spacing: 8px; font-size: 12px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #333333; background: #050505; }
QCheckBox::indicator:checked { background-color: #ffffff; border-color: #ffffff; }
QTabWidget::pane { border: 0; }
QTabBar::tab { background: transparent; color: #444444; font-weight: bold; padding: 10px 0px; margin-right: 25px; border: none; }
QTabBar::tab:selected { color: #ffffff; border-bottom: 2px solid #ffffff; }
QPushButton { background-color: #0a0a0a; color: #cccccc; border: 1px solid #1f1f1f; border-radius: 6px; padding: 8px 15px; font-weight: 600; }
QPushButton:hover { background-color: #151515; color: #ffffff; border-color: #444444; }
QPushButton.Primary { background-color: #ffffff; color: #000000; border: none; font-weight: 800; font-size: 13px; }
QPushButton.Primary:hover { background-color: #dddddd; color: #000000; }
QPushButton.Danger { background-color: #000000; border: 1px solid #8B0000; color: #FF4444; }
QPlainTextEdit { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; color: #666666; font-family: 'Consolas', monospace; font-size: 11px; }
QScrollBar:vertical { background: #050505; width: 6px; }
"""

STYLES_PRO = """
/* === TEMA PRO (Cyan & Atom Grey) === */
QMainWindow, QWidget#CentralWidget { background-color: #0f1115; }
QLabel { font-family: 'Segoe UI', sans-serif; color: #a0aab5; font-size: 13px; }
QLabel#Header { color: #ffffff; font-size: 16px; font-weight: bold; }
QFrame.Card { background-color: #161920; border: 1px solid #252830; border-radius: 12px; }
QLineEdit { background-color: #0f1115; border: 1px solid #2a2e38; border-radius: 8px; padding: 10px; color: #e0e6ed; font-size: 13px; selection-background-color: #00bcd4; }
QLineEdit:focus { border: 1px solid #00bcd4; background-color: #13151a; }
QListWidget { background-color: #0f1115; border: 1px solid #2a2e38; border-radius: 8px; color: #a0aab5; }
QCheckBox { color: #a0aab5; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 1px solid #353945; background: #0f1115; }
QCheckBox::indicator:checked { background-color: #00bcd4; border-color: #00bcd4; }
QTabWidget::pane { border: 0; }
QTabBar::tab { background: transparent; color: #656d79; font-weight: bold; padding: 12px 24px; border-bottom: 2px solid transparent; margin-right: 5px; }
QTabBar::tab:selected { color: #00bcd4; border-bottom: 2px solid #00bcd4; }
QPushButton { background-color: #252830; color: #ffffff; border: 1px solid #353945; border-radius: 8px; padding: 8px 16px; font-weight: 600; }
QPushButton:hover { background-color: #2f343f; border-color: #4c5260; }
QPushButton.Primary { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00bcd4, stop:1 #0097a7); border: none; color: #0f1115; font-weight: bold; font-size: 14px; }
QPushButton.Primary:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #26c6da, stop:1 #00acc1); }
QPushButton.Danger { background-color: #2a1515; border: 1px solid #5c2b2b; color: #ff6b6b; }
QPlainTextEdit { background-color: #0a0b0e; border: 1px solid #252830; border-radius: 8px; padding: 10px; font-family: 'Consolas', monospace; font-size: 12px; color: #98c379; }
QScrollBar:vertical { background: #0f1115; width: 8px; border-radius: 4px; }
"""

# ==============================================================================
# 🧩 COMPONENTES UI
# ==============================================================================

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(4)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(None) 

    def enable_shadow(self, enabled: bool):
        self.setGraphicsEffect(self.shadow_effect if enabled else None)

class TitleBarBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.parent.start_move(e)
    def mouseMoveEvent(self, e): self.parent.do_move(e)
    def mouseDoubleClickEvent(self, e): 
        if self.parent.isMaximized(): self.parent.showNormal()
        else: self.parent.showMaximized()

class XenoTitleBar(TitleBarBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(45)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        lbl_m = QLabel("PY-BUILDER"); lbl_m.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        lbl_s = QLabel(" STUDIO"); lbl_s.setStyleSheet("color: #666; font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_m); layout.addWidget(lbl_s); layout.addStretch()
        
        for char, func, color in [("—", parent.showMinimized, "#fff"), ("□", self.toggle, "#fff"), ("✕", parent.close, "#f00")]:
            btn = QPushButton(char)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background: transparent; border: none; color: #666; font-size: 14px;")
            btn.clicked.connect(func)
            layout.addWidget(btn)

    def toggle(self):
        if self.parent.isMaximized(): self.parent.showNormal()
        else: self.parent.showMaximized()

class ProTitleBar(TitleBarBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        lbl = QLabel("PY-BUILDER STUDIO"); lbl.setStyleSheet("color: #e0e6ed; font-weight: 900; font-size: 14px; letter-spacing: 1px;")
        badge = QLabel(" PRO "); badge.setStyleSheet("background: #00bcd4; color: black; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold;")
        layout.addWidget(lbl); layout.addSpacing(10); layout.addWidget(badge); layout.addStretch()
        
        for char, func in [("—", parent.showMinimized), ("▢", self.toggle), ("✕", parent.close)]:
            btn = QPushButton(char)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("background: transparent; border: none; color: #656d79; font-size: 16px; font-weight: bold;")
            btn.clicked.connect(func)
            layout.addWidget(btn)
            
    def toggle(self):
        if self.parent.isMaximized(): self.parent.showNormal()
        else: self.parent.showMaximized()

# ==============================================================================
# 🧵 LÓGICA DE FONDO
# ==============================================================================
class BuilderThread(QThread):
    log_message = Signal(str, str); finished = Signal(int)
    def __init__(self, command, parent=None):
        super().__init__(parent); self.command = command; self.is_running = True
    def run(self):
        try:
            cflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore', shell=False, creationflags=cflags)
            while self.is_running:
                line = process.stdout.readline()
                if line: self.log_message.emit(line.strip(), "info")
                elif process.poll() is not None: break
            if not self.is_running: process.terminate()
            self.finished.emit(process.wait())
        except Exception as e:
            self.log_message.emit(f"CRITICAL ERROR: {e}", "error"); self.finished.emit(-1)
    def stop(self): self.is_running = False

# ==============================================================================
# 🖥️ VENTANA PRINCIPAL
# ==============================================================================
class PyBuilderStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1050, 750)
        self.setMinimumSize(950, 650)
        
        self.old_pos = None
        self.thread = None
        self.current_theme = "XENO"
        self.card_refs = []

        self._init_ui()
        self._apply_theme()
        self._center_window()

    def _center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)

    def start_move(self, e): self.old_pos = e.globalPos()
    def do_move(self, e):
        if self.old_pos and not self.isMaximized():
            delta = QPoint(e.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = e.globalPos()

    def _init_ui(self):
        self.central = QWidget()
        self.central.setObjectName("CentralWidget")
        self.setCentralWidget(self.central)
        
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.title_bar_container = QWidget()
        self.main_layout.addWidget(self.title_bar_container) 
        
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(25, 10, 25, 25)
        content_layout.setSpacing(25)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self._ui_builder_tab(), "BUILDER")
        self.obfuscation_widget = ObfuscationWidget() 
        self.tabs.addTab(self.obfuscation_widget, "PROTECTION")
        left_col.addWidget(self.tabs)
        
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        
        console_card = Card(); self.card_refs.append(console_card)
        c_layout = QVBoxLayout(console_card)
        c_layout.setContentsMargins(1, 1, 1, 1)
        
        self.cons_header = QLabel("  EXECUTION LOG")
        self.cons_header.setFixedHeight(30)
        self.cons_header.setStyleSheet("background: transparent; color: #777; font-weight: bold; font-size: 11px;")
        
        self.log_console = QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFrameShape(QFrame.NoFrame)
        self.log_console.setPlaceholderText("Waiting for execution...")
        
        c_layout.addWidget(self.cons_header)
        c_layout.addWidget(self.log_console)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        
        actions_layout = QHBoxLayout()
        self.btn_build = QPushButton("INITIALIZE BUILD")
        self.btn_build.setProperty("class", "Primary")
        self.btn_build.setMinimumHeight(45)
        self.btn_build.setCursor(Qt.PointingHandCursor)
        self.btn_build.clicked.connect(self._start_build)
        
        self.btn_cancel = QPushButton("STOP")
        self.btn_cancel.setProperty("class", "Danger")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_build)
        
        actions_layout.addWidget(self.btn_build, 1)
        actions_layout.addWidget(self.btn_cancel, 1)
        
        footer_layout = QHBoxLayout()
        self.btn_theme = QPushButton("☯ Switch Theme")
        self.btn_theme.setFixedWidth(120)
        self.btn_theme.clicked.connect(self._toggle_theme_logic)
        
        self.btn_save = QPushButton("Save"); self.btn_save.setFixedWidth(80); self.btn_save.clicked.connect(self._save_config)
        self.btn_load = QPushButton("Load"); self.btn_load.setFixedWidth(80); self.btn_load.clicked.connect(self._load_config)
        
        footer_layout.addWidget(self.btn_theme)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_load)
        footer_layout.addWidget(self.btn_save)

        right_col.addWidget(console_card, 1)
        right_col.addWidget(self.progress_bar)
        right_col.addLayout(actions_layout)
        right_col.addLayout(footer_layout)

        content_layout.addLayout(left_col, 45)
        content_layout.addLayout(right_col, 55)
        self.main_layout.addWidget(content_area)
        
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setStyleSheet("width: 15px; height: 15px; background: transparent;")

    def _ui_builder_tab(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 15, 0, 0); layout.setSpacing(15)
        
        c1 = Card(); self.card_refs.append(c1)
        l1 = QVBoxLayout(c1)
        l1.addWidget(QLabel("SOURCE & OUTPUT", objectName="Header"))
        l1.addSpacing(5)
        self.script_edit = QLineEdit(); self.script_edit.setPlaceholderText("Script Path (.py)")
        b1 = QPushButton("..."); b1.setFixedWidth(40); b1.clicked.connect(self._select_script)
        h1 = QHBoxLayout(); h1.addWidget(self.script_edit); h1.addWidget(b1)
        self.out_edit = QLineEdit(); self.out_edit.setPlaceholderText("Output Folder")
        b2 = QPushButton("..."); b2.setFixedWidth(40); b2.clicked.connect(self._select_output_dir)
        h2 = QHBoxLayout(); h2.addWidget(self.out_edit); h2.addWidget(b2)
        self.name_edit = QLineEdit(); self.name_edit.setPlaceholderText("Exe Name")
        l1.addLayout(h1); l1.addLayout(h2); l1.addWidget(self.name_edit)
        
        c2 = Card(); self.card_refs.append(c2)
        l2 = QVBoxLayout(c2)
        l2.addWidget(QLabel("FLAGS", objectName="Header")); l2.addSpacing(5)
        self.chk_onefile = QCheckBox("One File Bundle (--onefile)")
        self.chk_noconsole = QCheckBox("No Console (--noconsole)")
        self.chk_clean = QCheckBox("Clean Build Cache")
        self.chk_onefile.setChecked(True); self.chk_noconsole.setChecked(True)
        l2.addWidget(self.chk_onefile); l2.addWidget(self.chk_noconsole); l2.addWidget(self.chk_clean)
        
        c3 = Card(); self.card_refs.append(c3)
        l3 = QVBoxLayout(c3)
        l3.addWidget(QLabel("EMBEDDED ASSETS", objectName="Header")); l3.addSpacing(5)
        self.icon_edit = QLineEdit(); self.icon_edit.setPlaceholderText("Icon (.ico)")
        b3 = QPushButton("..."); b3.setFixedWidth(40); b3.clicked.connect(self._select_icon)
        h3 = QHBoxLayout(); h3.addWidget(self.icon_edit); h3.addWidget(b3)
        self.data_list = QListWidget(); self.data_list.setFixedHeight(70)
        h_btns = QHBoxLayout()
        b_addf = QPushButton("+ File"); b_addf.clicked.connect(self._add_data_file)
        b_addd = QPushButton("+ Folder"); b_addd.clicked.connect(self._add_data_folder)
        b_del = QPushButton("Del"); b_del.clicked.connect(self._remove_data_item)
        h_btns.addWidget(b_addf); h_btns.addWidget(b_addd); h_btns.addStretch(); h_btns.addWidget(b_del)
        l3.addLayout(h3); l3.addWidget(self.data_list); l3.addLayout(h_btns)
        
        layout.addWidget(c1); layout.addWidget(c2); layout.addWidget(c3); layout.addStretch()
        return container

    def _toggle_theme_logic(self):
        if self.current_theme == "XENO": self.current_theme = "PRO"
        else: self.current_theme = "XENO"
        self._apply_theme()

    def _apply_theme(self):
        if self.current_theme == "XENO":
            self.setStyleSheet(STYLES_XENO)
            self.btn_theme.setText("☾ Mode: XENO")
            self.progress_bar.setStyleSheet("background: #111; border: none;")
        else:
            self.setStyleSheet(STYLES_PRO)
            self.btn_theme.setText("☀ Mode: PRO")
            self.progress_bar.setStyleSheet("background: #252830; border-radius: 2px;")
            
        if self.main_layout.count() > 0:
            item = self.main_layout.itemAt(0)
            if item.widget():
                item.widget().deleteLater()
                self.main_layout.removeItem(item)
        
        if self.current_theme == "XENO": self.title_bar = XenoTitleBar(self)
        else: self.title_bar = ProTitleBar(self)
        self.main_layout.insertWidget(0, self.title_bar)
        
        for card in self.card_refs:
            if self.current_theme == "XENO":
                card.enable_shadow(False)
                if card.layout(): card.layout().setContentsMargins(1,1,1,1)
            else:
                card.enable_shadow(True)
                if card.layout(): card.layout().setContentsMargins(15,15,15,15)
        
        if self.current_theme == "XENO": self.cons_header.setVisible(True)
        else: self.cons_header.setVisible(False)

    def resizeEvent(self, e):
        r = self.rect()
        self.sizegrip.move(r.right()-15, r.bottom()-15)
        super().resizeEvent(e)

    def _start_build(self):
        script = self.script_edit.text(); out = self.out_edit.text()
        if not script or not out: QMessageBox.warning(self, "Error", "Missing paths."); return
        
        self.log_console.clear(); self._set_ui_state(busy=True)
        self._log("> INITIALIZING...", "info")
        
        obf = self.obfuscation_widget.get_options(); target = script
        if obf["enabled"]:
            self._log(f"> Obfuscating with {obf['engine']}...", "info")
            try: QApplication.processEvents(); target = run_obfuscator(script, out, obf); self._log("> Obfuscation done.", "success")
            except Exception as e: self._log(f"> Error: {e}", "error"); self._build_finished(-1); return

        opts = self._get_options(); opts["script_path"] = target
        cmd = build_pyinstaller_command(opts)
        self._log("> Starting Compiler...", "info")
        self.thread = BuilderThread(cmd)
        self.thread.log_message.connect(self._log); self.thread.finished.connect(self._build_finished)
        self.thread.start()

    def _build_finished(self, code):
        self._set_ui_state(busy=False)
        if code == 0: 
            self._log("> SUCCESS.", "success"); QMessageBox.information(self, "OK", "Build Complete.")
            try: shutil.rmtree(os.path.join(self.out_edit.text(), "temp_ast_build"), ignore_errors=True)
            except: pass
        else: self._log("> FAILED.", "error"); QMessageBox.critical(self, "Fail", "Build Failed.")

    def _cancel_build(self):
        if self.thread and self.thread.isRunning(): self.thread.stop(); self._log("> Aborted.", "error")

    def _set_ui_state(self, busy):
        self.btn_build.setVisible(not busy); self.btn_cancel.setVisible(busy)
        self.progress_bar.setVisible(busy); self.progress_bar.setRange(0, 0) if busy else self.progress_bar.setRange(0, 100)
        self.tabs.setEnabled(not busy); self.title_bar.setEnabled(not busy)

    def _log(self, msg, type="info"):
        cursor = self.log_console.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        if type=="error": fmt.setForeground(QColor("#ff4444" if self.current_theme=="XENO" else "#ff6b6b"))
        elif type=="success": fmt.setForeground(QColor("#ffffff" if self.current_theme=="XENO" else "#00bcd4")); fmt.setFontWeight(QFont.Bold)
        else: fmt.setForeground(QColor("#888888" if self.current_theme=="XENO" else "#a0aab5"))
        cursor.mergeCharFormat(fmt); cursor.insertText(msg+"\n"); self.log_console.setTextCursor(cursor)

    # ==============================================================================
    # 📝 DIALOGOS Y GETTERS CORREGIDOS (EXPANDIDOS)
    # ==============================================================================
    def _get_options(self):
        return {
            "script_path": self.script_edit.text(),
            "output_dir": self.out_edit.text(),
            "exe_name": self.name_edit.text(),
            "one_file": self.chk_onefile.isChecked(),
            "no_console": self.chk_noconsole.isChecked(),
            "clean": self.chk_clean.isChecked(),
            "icon_path": self.icon_edit.text(),
            "data_files": [self.data_list.item(i).text() for i in range(self.data_list.count())]
        }

    def _select_script(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Script", "", "Python (*.py *.pyw)")
        if f:
            self.script_edit.setText(f)
            self.name_edit.setText(Path(f).stem)
            self.out_edit.setText(str(Path(f).parent))

    def _select_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output")
        if d:
            self.out_edit.setText(d)

    def _select_icon(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon (*.ico)")
        if f:
            self.icon_edit.setText(f)

    def _add_data_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select File")
        if f:
            self.data_list.addItem(f)

    def _add_data_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder")
        if d:
            self.data_list.addItem(d)

    def _remove_data_item(self):
        for i in self.data_list.selectedItems():
            self.data_list.takeItem(self.data_list.row(i))

    def _save_config(self):
        f, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "JSON (*.json)")
        if f:
            d = self._get_options()
            d.update(self.obfuscation_widget.get_options())
            with open(f, 'w') as o:
                json.dump(d, o, indent=4)

    def _load_config(self):
        f, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON (*.json)")
        if f:
            try:
                with open(f, 'r') as o:
                    d = json.load(o)
                self.script_edit.setText(d.get("script_path", ""))
                self.out_edit.setText(d.get("output_dir", ""))
                self.name_edit.setText(d.get("exe_name", ""))
                self.chk_onefile.setChecked(d.get("one_file", True))
                self.chk_noconsole.setChecked(d.get("no_console", True))
                self.chk_clean.setChecked(d.get("clean", False))
                self.icon_edit.setText(d.get("icon_path", ""))
                self.data_list.clear()
                for x in d.get("data_files", []):
                    self.data_list.addItem(x)
                if "enabled" in d:
                    self.obfuscation_widget.enable_check.setChecked(d["enabled"])
            except Exception as e:
                print(e)

    def closeEvent(self, e): 
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        e.accept()