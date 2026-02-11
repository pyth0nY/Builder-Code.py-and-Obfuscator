import sys
import os
import subprocess
import json
import shutil
from pathlib import Path

# --- FIX DE RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(current_dir)             
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
    QLineEdit, QPushButton, QCheckBox, QListWidget, 
    QPlainTextEdit, QProgressBar, QStackedWidget, QFileDialog, 
    QMessageBox, QLabel, QTabWidget, QSizeGrip, QApplication,
    QGraphicsDropShadowEffect, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QPoint, QSize, QUrl
from PySide6.QtGui import (
    QColor, QTextCharFormat, QFont, QTextCursor, QPalette, QIcon, QPixmap, QDesktopServices
)

from engines.pyinstaller_engine import build_command as build_pyinstaller_command
from engines.obfuscation_engine import run_obfuscator
from ui.obfuscation_widget import ObfuscationWidget
from ui.license_widget import LicenseWidget 

# ==============================================================================
# 🖼️ ICON HELPER
# ==============================================================================
class IconHelper:
    @staticmethod
    def get(name, color="#000000", size=24):
        try:
            from pytablericons import TablerIcons, OutlineIcon
            from PIL.ImageQt import ImageQt
            attr_name = name.replace("-", "_").upper()
            if hasattr(OutlineIcon, attr_name):
                icon_enum = getattr(OutlineIcon, attr_name)
                pil_img = TablerIcons.load(icon_enum, color=color, size=size)
                return QIcon(QPixmap.fromImage(ImageQt(pil_img)))
        except ImportError: pass
        except Exception: pass
        return QIcon()

# ==============================================================================
# 🎨 ESTILOS CSS - TEMAS ORIGINALES
# ==============================================================================

STYLES_LUMINA = """
/* === TEMA LUMINA (Light Mode) === */
QMainWindow, QWidget#CentralWidget { background-color: #F8F9FA; }
QLabel { font-family: 'Segoe UI', sans-serif; color: #495057; font-size: 13px; font-weight: 500; }
QLabel#Header { color: #212529; font-size: 15px; font-weight: 700; letter-spacing: 0.3px; }
QFrame.Card { background-color: #FFFFFF; border: 1px solid #E9ECEF; border-radius: 12px; }
QLineEdit, QSpinBox { background-color: #FFFFFF; border: 1px solid #DEE2E6; border-radius: 8px; padding: 10px; color: #212529; selection-background-color: #3B82F6; }
QLineEdit:focus, QSpinBox:focus { border: 1px solid #3B82F6; }
QListWidget { background-color: #FFFFFF; border: 1px solid #DEE2E6; border-radius: 8px; color: #495057; padding: 5px; }
QCheckBox { color: #495057; spacing: 8px; }
QComboBox { background-color: #FFFFFF; color: #212529; border: 1px solid #DEE2E6; padding: 6px; border-radius: 6px; }
QComboBox QAbstractItemView { background-color: #FFFFFF; color: #212529; selection-background-color: #EFF6FF; }
QGroupBox { font-weight: bold; border: 1px solid #DEE2E6; border-radius: 8px; margin-top: 20px; color: #495057; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QTabWidget::pane { border: 0; }
QTabBar::tab { color: #6C757D; font-weight: 600; padding: 10px 20px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #3B82F6; border-bottom: 2px solid #3B82F6; background-color: #EFF6FF; border-top-left-radius: 6px; border-top-right-radius: 6px;}
QPushButton { background-color: #FFFFFF; color: #495057; border: 1px solid #DEE2E6; border-radius: 8px; padding: 8px 16px; font-weight: 600; text-align: left; }
QPushButton:hover { background-color: #F1F3F5; color: #212529; border-color: #CED4DA; }
QPushButton.Primary { background-color: #3B82F6; color: #FFFFFF; border: none; font-weight: 700; text-align: center; }
QPushButton.Primary:hover { background-color: #2563EB; }
QPushButton.Danger { background-color: #FEF2F2; border: 1px solid #FECACA; color: #DC2626; text-align: center; }
QPushButton.IconOnly { padding: 5px; border: none; background: transparent; }
QPushButton.IconOnly:hover { background: #E9ECEF; border-radius: 4px; }
QPlainTextEdit { background-color: #1E1E1E; border: 1px solid #DEE2E6; border-radius: 8px; color: #E0E0E0; font-family: 'Consolas', monospace; }
QScrollBar:vertical { background: #F8F9FA; width: 8px; }
"""

STYLES_XENO = """
/* === TEMA XENO (Fixed Dark Mode) === */
QMainWindow, QWidget#CentralWidget { background-color: #050505; }
QWidget { background-color: transparent; color: #e0e0e0; }
QLabel { font-family: 'Segoe UI', sans-serif; color: #888888; font-size: 13px; font-weight: 500; background: transparent; }
QLabel#Header { color: #ffffff; font-size: 14px; font-weight: bold; }
QFrame.Card { background-color: #0a0a0a; border: 1px solid #1f1f1f; border-radius: 8px; }
QLineEdit, QSpinBox { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; padding: 10px; color: #ffffff; }
QLineEdit:focus, QSpinBox:focus { border: 1px solid #555555; background-color: #080808; }
QListWidget { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; color: #cccccc; }
QComboBox { background-color: #050505; color: #fff; border: 1px solid #1f1f1f; padding: 5px; border-radius: 4px; }
QComboBox QAbstractItemView { background-color: #050505; selection-background-color: #333; color: #fff; border: 1px solid #333; }
QGroupBox { border: 1px solid #1f1f1f; border-radius: 6px; margin-top: 20px; font-weight: bold; color: #aaaaaa; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QCheckBox { color: #999999; spacing: 8px; background: transparent; }
QCheckBox::indicator { border: 1px solid #333; background: #000; border-radius: 2px; width: 14px; height: 14px; }
QCheckBox::indicator:checked { background-color: #fff; border-color: #fff; }
QTabWidget::pane { border: 0; }
QTabBar::tab { color: #444444; font-weight: bold; padding: 10px 0px; margin-right: 25px; border: none; background: transparent; }
QTabBar::tab:selected { color: #ffffff; border-bottom: 2px solid #ffffff; }
QPushButton { background-color: #0a0a0a; color: #cccccc; border: 1px solid #1f1f1f; border-radius: 6px; font-weight: 600; text-align: left; }
QPushButton:hover { background-color: #151515; color: #ffffff; border-color: #444444; }
QPushButton.Primary { background-color: #ffffff; color: #000000; border: none; font-weight: 800; text-align: center; }
QPushButton.Danger { background-color: #000000; border: 1px solid #8B0000; color: #FF4444; text-align: center; }
QPushButton.IconOnly { padding: 5px; border: none; background: transparent; }
QPushButton.IconOnly:hover { background: #222; border-radius: 4px; }
QPlainTextEdit { background-color: #050505; border: 1px solid #1f1f1f; border-radius: 6px; color: #666666; }
QScrollBar:vertical { background: #050505; width: 6px; }
QScrollBar::handle:vertical { background: #333; border-radius: 3px; }
"""

# ==============================================================================
# 🧩 COMPONENTES UI
# ==============================================================================

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20); self.shadow.setXOffset(0); self.shadow.setYOffset(4)
        self.shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(None) 

    def enable_shadow(self, enabled: bool, color=QColor(0,0,0,20)):
        if enabled:
            self.shadow.setColor(color); self.setGraphicsEffect(self.shadow)
        else:
            self.setGraphicsEffect(None)

class TitleBarBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton: self.parent.start_move(e)
    def mouseMoveEvent(self, e): self.parent.do_move(e)

class LuminaTitleBar(TitleBarBase):
    def __init__(self, parent):
        super().__init__(parent); self.setFixedHeight(50)
        layout = QHBoxLayout(self); layout.setContentsMargins(25, 0, 20, 0)
        lbl = QLabel("PyBuilder Studio"); lbl.setStyleSheet("color: #1F2937; font-weight: 800; font-size: 15px;")
        layout.addWidget(lbl); layout.addStretch()
        for ic, func in [("minus", parent.showMinimized), ("square", lambda: parent.showNormal() if parent.isMaximized() else parent.showMaximized()), ("x", parent.close)]:
            btn = QPushButton(); btn.setIcon(IconHelper.get(ic, "#6B7280")); btn.setFixedSize(35, 30); btn.setProperty("class", "IconOnly")
            btn.clicked.connect(func); layout.addWidget(btn)

class XenoTitleBar(TitleBarBase):
    def __init__(self, parent):
        super().__init__(parent); self.setFixedHeight(45)
        layout = QHBoxLayout(self); layout.setContentsMargins(20, 0, 20, 0)
        lbl = QLabel("PY-BUILDER"); lbl.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(lbl); layout.addStretch()
        for ic, func in [("minus", parent.showMinimized), ("square", lambda: parent.showNormal() if parent.isMaximized() else parent.showMaximized()), ("x", parent.close)]:
            btn = QPushButton(); btn.setIcon(IconHelper.get(ic, "#888888")); btn.setFixedSize(35, 30); btn.setProperty("class", "IconOnly")
            btn.clicked.connect(func); layout.addWidget(btn)

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
            self.log_message.emit(f"ERROR: {e}", "error"); self.finished.emit(-1)
    def stop(self): self.is_running = False

class PyBuilderStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint); self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1080, 780); self.setMinimumSize(950, 650)
        self.old_pos = None; self.thread = None; self.current_theme = "LUMINA"; self.card_refs = []; self.ui_buttons = {}
        self._init_ui(); self._apply_theme(); self._center_window()

    def _center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width()-self.width())//2, (screen.height()-self.height())//2)

    def start_move(self, e): self.old_pos = e.globalPos()
    def do_move(self, e):
        if self.old_pos and not self.isMaximized():
            delta = QPoint(e.globalPos() - self.old_pos); self.move(self.x() + delta.x(), self.y() + delta.y()); self.old_pos = e.globalPos()

    def _init_ui(self):
        self.central = QWidget(); self.central.setObjectName("CentralWidget"); self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.title_bar_container = QWidget(); self.main_layout.addWidget(self.title_bar_container) 
        content_area = QWidget(); content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(25, 10, 25, 25); content_layout.setSpacing(25)
        
        left_col = QVBoxLayout(); left_col.setSpacing(20)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._ui_builder_tab(), "BUILDER")
        self.obfuscation_widget = ObfuscationWidget(); self.tabs.addTab(self.obfuscation_widget, "PROTECTION")
        
        # --- TAB LICENCIA ---
        self.license_widget = LicenseWidget(); self.tabs.addTab(self.license_widget, "LICENSE")
        self.card_refs.append(self.license_widget.card_info); self.card_refs.append(self.license_widget.card_credits)

        left_col.addWidget(self.tabs); left_col.addStretch()
        
        left_footer = QHBoxLayout()
        self.btn_github = QPushButton(" pyth0nY"); self.btn_github.setFixedWidth(100); self.btn_github.setCursor(Qt.PointingHandCursor)
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/pyth0nY")))
        self.ui_buttons["github"] = self.btn_github
        left_footer.addWidget(self.btn_github); left_footer.addStretch(); left_col.addLayout(left_footer)
        
        right_col = QVBoxLayout(); right_col.setSpacing(15)
        console_card = Card(); self.card_refs.append(console_card)
        c_layout = QVBoxLayout(console_card); c_layout.setContentsMargins(15, 15, 15, 15)
        self.cons_header = QLabel("EXECUTION LOG"); self.cons_header.setFixedHeight(20)
        self.log_console = QPlainTextEdit(); self.log_console.setReadOnly(True); self.log_console.setFrameShape(QFrame.NoFrame)
        c_layout.addWidget(self.cons_header); c_layout.addWidget(self.log_console)
        
        self.progress_bar = QProgressBar(); self.progress_bar.setFixedHeight(4); self.progress_bar.setVisible(False)
        actions_layout = QHBoxLayout()
        self.btn_build = QPushButton(" INITIALIZE BUILD"); self.btn_build.setProperty("class", "Primary"); self.btn_build.setMinimumHeight(45)
        self.btn_build.clicked.connect(self._start_build)
        self.btn_cancel = QPushButton(" STOP"); self.btn_cancel.setProperty("class", "Danger"); self.btn_cancel.setMinimumHeight(45); self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_build)
        actions_layout.addWidget(self.btn_build, 1); actions_layout.addWidget(self.btn_cancel, 1)
        
        footer_layout = QHBoxLayout()
        self.btn_theme = QPushButton("Theme"); self.btn_theme.setFixedWidth(120); self.btn_theme.clicked.connect(self._toggle_theme_logic)
        self.btn_save = QPushButton("Save"); self.btn_save.setFixedWidth(90); self.btn_save.clicked.connect(self._save_config)
        self.btn_load = QPushButton("Load"); self.btn_load.setFixedWidth(90); self.btn_load.clicked.connect(self._load_config)
        
        self.ui_buttons.update({"build":self.btn_build, "cancel":self.btn_cancel, "theme":self.btn_theme, "save":self.btn_save, "load":self.btn_load})
        footer_layout.addWidget(self.btn_theme); footer_layout.addStretch(); footer_layout.addWidget(self.btn_load); footer_layout.addWidget(self.btn_save)

        right_col.addWidget(console_card, 1); right_col.addWidget(self.progress_bar); right_col.addLayout(actions_layout); right_col.addLayout(footer_layout)
        content_layout.addLayout(left_col, 45); content_layout.addLayout(right_col, 55); self.main_layout.addWidget(content_area)
        self.sizegrip = QSizeGrip(self)

    def _ui_builder_tab(self):
        container = QWidget(); layout = QVBoxLayout(container); layout.setContentsMargins(0, 15, 0, 0); layout.setSpacing(15)
        c1 = Card(); self.card_refs.append(c1); l1 = QVBoxLayout(c1); l1.setContentsMargins(20, 20, 20, 20); l1.setSpacing(12)
        l1.addWidget(QLabel("PROJECT SETTINGS", objectName="Header"))
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["⚡ Single File Mode", "🔥 Full Project Mode"]); self.mode_combo.setCurrentIndex(1) 
        l1.addWidget(QLabel("Build Mode:")); l1.addWidget(self.mode_combo)
        l1.addWidget(QLabel("Entry Point Script:"))
        self.script_edit = QLineEdit(); self.script_edit.setPlaceholderText("Path to main.py...")
        b1 = QPushButton("Browse"); b1.setFixedWidth(85); b1.clicked.connect(self._select_script); self.ui_buttons["browse_script"] = b1
        h1 = QHBoxLayout(); h1.addWidget(self.script_edit); h1.addWidget(b1); l1.addLayout(h1)
        
        h_row = QHBoxLayout()
        v_out = QVBoxLayout(); v_out.setSpacing(5); v_out.addWidget(QLabel("Output Folder:"))
        self.out_edit = QLineEdit(); self.out_edit.setPlaceholderText("Select output directory...")
        b2 = QPushButton(); b2.setFixedWidth(40); b2.clicked.connect(self._select_output_dir); self.ui_buttons["browse_out"] = b2
        hh = QHBoxLayout(); hh.addWidget(self.out_edit); hh.addWidget(b2); v_out.addLayout(hh)
        v_name = QVBoxLayout(); v_name.setSpacing(5); v_name.addWidget(QLabel("Executable Name:"))
        self.name_edit = QLineEdit(); self.name_edit.setPlaceholderText("MyApp"); v_name.addWidget(self.name_edit)
        h_row.addLayout(v_out, 2); h_row.addLayout(v_name, 1); l1.addLayout(h_row)
        
        c2 = Card(); self.card_refs.append(c2); l2 = QVBoxLayout(c2); l2.setContentsMargins(20, 20, 20, 20); l2.setSpacing(10)
        l2.addWidget(QLabel("COMPILER FLAGS", objectName="Header"))
        self.chk_onefile = QCheckBox("One File Bundle"); self.chk_noconsole = QCheckBox("No Console")
        self.chk_clean = QCheckBox("Clean Build"); self.chk_upx = QCheckBox("Use UPX")
        self.chk_onefile.setChecked(True); self.chk_noconsole.setChecked(True)
        g = QHBoxLayout(); c1v = QVBoxLayout(); c1v.addWidget(self.chk_onefile); c1v.addWidget(self.chk_noconsole)
        c2v = QVBoxLayout(); c2v.addWidget(self.chk_clean); c2v.addWidget(self.chk_upx)
        g.addLayout(c1v); g.addLayout(c2v); l2.addLayout(g)

        c3 = Card(); self.card_refs.append(c3); l3 = QVBoxLayout(c3); l3.setContentsMargins(20, 20, 20, 20)
        l3.addWidget(QLabel("ASSETS & ICON", objectName="Header"))
        self.icon_edit = QLineEdit(); b3 = QPushButton("Browse"); b3.setFixedWidth(85); b3.clicked.connect(self._select_icon); self.ui_buttons["browse_icon"] = b3
        h3 = QHBoxLayout(); h3.addWidget(self.icon_edit); h3.addWidget(b3); l3.addLayout(h3)
        self.data_list = QListWidget(); self.data_list.setFixedHeight(60)
        hb = QHBoxLayout(); baf = QPushButton("File"); bad = QPushButton("Folder"); br = QPushButton("Remove")
        self.ui_buttons.update({"add_file":baf, "add_folder":bad, "remove_asset":br})
        baf.clicked.connect(self._add_data_file); bad.clicked.connect(self._add_data_folder); br.clicked.connect(self._remove_data_item)
        hb.addWidget(baf); hb.addWidget(bad); hb.addStretch(); hb.addWidget(br); l3.addWidget(self.data_list); l3.addLayout(hb)
        
        layout.addWidget(c1); layout.addWidget(c2); layout.addWidget(c3); layout.addStretch(); return container

    def _toggle_theme_logic(self):
        self.current_theme = "XENO" if self.current_theme == "LUMINA" else "LUMINA"; self._apply_theme()

    def _apply_theme(self):
        if self.current_theme == "XENO":
            self.setStyleSheet(STYLES_XENO); ic = "#CCCCCC"; ai = "#FFFFFF"
            if self.main_layout.count() > 0:
                it = self.main_layout.itemAt(0); it.widget().deleteLater(); self.main_layout.removeItem(it)
            self.title_bar = XenoTitleBar(self); self.main_layout.insertWidget(0, self.title_bar)
            for card in self.card_refs:
                if hasattr(card, 'enable_shadow'): card.enable_shadow(False)
                if card.layout(): card.layout().setContentsMargins(1,1,1,1)
        else:
            self.setStyleSheet(STYLES_LUMINA); ic = "#495057"; ai = "#3B82F6"
            if self.main_layout.count() > 0:
                it = self.main_layout.itemAt(0); it.widget().deleteLater(); self.main_layout.removeItem(it)
            self.title_bar = LuminaTitleBar(self); self.main_layout.insertWidget(0, self.title_bar)
            for card in self.card_refs:
                if hasattr(card, 'enable_shadow'): card.enable_shadow(True, QColor(0,0,0,15))
                if card.layout(): card.layout().setContentsMargins(20,20,20,20)
        
        if hasattr(self, 'license_widget'): self.license_widget.update_theme_style(self.current_theme)
        self.ui_buttons["github"].setIcon(IconHelper.get("brand-github", ic))
        self.ui_buttons["build"].setIcon(IconHelper.get("player-play", "#FFFFFF"))
        self.ui_buttons["theme"].setIcon(IconHelper.get("moon" if self.current_theme == "XENO" else "sun", ic))
        self.ui_buttons["save"].setIcon(IconHelper.get("device-floppy", ic)); self.ui_buttons["load"].setIcon(IconHelper.get("folder-open", ic))
        self.ui_buttons["browse_script"].setIcon(IconHelper.get("file-code", ic)); self.ui_buttons["browse_out"].setIcon(IconHelper.get("folder", ic))
        self.ui_buttons["browse_icon"].setIcon(IconHelper.get("photo", ic)); self.ui_buttons["add_file"].setIcon(IconHelper.get("file-plus", ic))
        self.ui_buttons["add_folder"].setIcon(IconHelper.get("folder-plus", ic)); self.ui_buttons["remove_asset"].setIcon(IconHelper.get("trash", "#FF4444" if self.current_theme=="XENO" else "#DC2626"))
        self.tabs.setTabIcon(0, IconHelper.get("package", ai)); self.tabs.setTabIcon(1, IconHelper.get("shield-lock", ai)); self.tabs.setTabIcon(2, IconHelper.get("certificate", ai))

    def _start_build(self):
        s, o = self.script_edit.text(), self.out_edit.text()
        if not s or not o: QMessageBox.warning(self, "Attention", "Paths missing."); return
        self.log_console.clear(); self._set_ui_state(True)
        ir = (self.mode_combo.currentIndex() == 1)
        opts = self.obfuscation_widget.get_options(); opts["recursive"] = ir; fsp = s
        if opts["enabled"]:
            try: QApplication.processEvents(); fsp = run_obfuscator(s, o, opts); self._log("> Obfuscation Success", "success")
            except Exception as e: self._log(f"> Error: {e}", "error"); self._build_finished(-1); return
        self.thread = BuilderThread(build_pyinstaller_command({"script_path":fsp, "output_dir":o, "exe_name":self.name_edit.text(), "one_file":self.chk_onefile.isChecked(), "no_console":self.chk_noconsole.isChecked(), "clean":self.chk_clean.isChecked(), "icon_path":self.icon_edit.text(), "data_files":[self.data_list.item(i).text() for i in range(self.data_list.count())]}))
        self.thread.log_message.connect(self._log); self.thread.finished.connect(self._build_finished); self.thread.start()

    def _build_finished(self, code):
        self._set_ui_state(False); self._log("> Done.", "success" if code==0 else "error")
    def _cancel_build(self):
        if self.thread: self.thread.stop(); self._log("> Aborted", "error")
    def _set_ui_state(self, busy):
        self.btn_build.setVisible(not busy); self.btn_cancel.setVisible(busy); self.progress_bar.setVisible(busy); self.tabs.setEnabled(not busy)
    def _log(self, msg, type="info"):
        c = self.log_console.textCursor(); c.movePosition(QTextCursor.End); f = QTextCharFormat()
        f.setForeground(QColor("#FF5252" if type=="error" else "#69F0AE" if type=="success" else "#E0E0E0")); c.mergeCharFormat(f); c.insertText(msg+"\n")
    def _select_script(self): f, _ = QFileDialog.getOpenFileName(self, "Script", "", "Python (*.py)"); self.script_edit.setText(f)
    def _select_output_dir(self): self.out_edit.setText(QFileDialog.getExistingDirectory(self, "Output"))
    def _select_icon(self): f, _ = QFileDialog.getOpenFileName(self, "Icon", "", "Icon (*.ico)"); self.icon_edit.setText(f)
    def _add_data_file(self): f, _ = QFileDialog.getOpenFileName(self); self.data_list.addItem(f)
    def _add_data_folder(self): self.data_list.addItem(QFileDialog.getExistingDirectory(self))
    def _remove_data_item(self): [self.data_list.takeItem(self.data_list.row(i)) for i in self.data_list.selectedItems()]
    def _save_config(self): pass
    def _load_config(self): pass
    def closeEvent(self, e): e.accept()