# Contenido COMPLETO y ESTABLE para: ui/main_window.py

import sys, os, subprocess, json, shutil
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QColor, QTextCharFormat, QFont, QPalette, QTextCursor
from engines.pyinstaller_engine import build_command as build_pyinstaller_command
from engines.obfuscation_engine import run_obfuscator
from ui.obfuscation_widget import ObfuscationWidget

class BuilderThread(QThread):
    log_message = Signal(str, str); finished = Signal(int)
    def __init__(self, command, parent=None):
        super().__init__(parent); self.command = command; self.is_running = True
    def run(self):
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore', shell=False, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            while self.is_running:
                line = process.stdout.readline()
                if line: self.log_message.emit(line.strip(), "info")
                elif process.poll() is not None: break
            if not self.is_running: process.terminate()
            self.finished.emit(process.wait())
        except Exception as e:
            self.log_message.emit(f"FATAL ERROR: Could not run command: {e}", "error"); self.finished.emit(-1)
    def stop(self): self.is_running = False

class PyBuilderStudio(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Py-Builder Studio"); self.setMinimumSize(950, 800)
        self.setWindowIcon(QIcon.fromTheme("utilities-terminal")); self.thread = None
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget(); main_layout = QVBoxLayout(central_widget)
        self.tabs = QTabWidget(); main_layout.addWidget(self.tabs)
        self.tabs.addTab(self._create_builder_widget(), QIcon.fromTheme("applications-engineering"), "Empaquetador")
        self.obfuscation_widget = ObfuscationWidget(); self.tabs.addTab(self.obfuscation_widget, QIcon.fromTheme("dialog-password"), "Seguridad")
        self.setCentralWidget(central_widget); self.setStatusBar(QStatusBar(self))

    def _create_builder_widget(self):
        container = QWidget(); main_layout = QHBoxLayout(container)
        left_frame = self._create_left_column(); right_frame = self._create_right_column()
        main_layout.addWidget(left_frame, 2); main_layout.addWidget(right_frame, 3)
        self._connect_signals(); return container
    def _create_left_column(self):
        frame = QFrame(); layout = QVBoxLayout(frame); layout.setSpacing(15); io_group = QGroupBox("Archivos"); io_layout = QFormLayout(io_group)
        self.script_edit = QLineEdit(); self.output_dir_edit = QLineEdit(); self.exe_name_edit = QLineEdit()
        self.script_btn = QPushButton("Script...", icon=QIcon.fromTheme("document-open")); self.output_dir_btn = QPushButton("Salida...", icon=QIcon.fromTheme("folder-open"))
        io_layout.addRow(self.script_btn, self.script_edit); io_layout.addRow(self.output_dir_btn, self.output_dir_edit); io_layout.addRow("Nombre del .exe:", self.exe_name_edit)
        opts_group = QGroupBox("Opciones"); opts_layout = QVBoxLayout(opts_group)
        self.one_file_check = QCheckBox("Un solo archivo"); self.no_console_check = QCheckBox("App de Ventana"); self.clean_check = QCheckBox("Limpiar Build")
        self.one_file_check.setChecked(True); self.no_console_check.setChecked(True)
        opts_layout.addWidget(self.one_file_check); opts_layout.addWidget(self.no_console_check); opts_layout.addWidget(self.clean_check)
        assets_group = QGroupBox("Assets"); assets_layout = QVBoxLayout(assets_group)
        icon_layout = QHBoxLayout(); self.icon_edit = QLineEdit(); self.icon_btn = QPushButton(icon=QIcon.fromTheme("image-x-generic")); icon_layout.addWidget(self.icon_edit); icon_layout.addWidget(self.icon_btn)
        self.data_list = QListWidget(); data_btns = QHBoxLayout(); self.add_file_btn = QPushButton("Archivo"); self.add_folder_btn = QPushButton("Carpeta"); self.remove_data_btn = QPushButton("Quitar")
        data_btns.addWidget(self.add_file_btn); data_btns.addWidget(self.add_folder_btn); data_btns.addStretch(); data_btns.addWidget(self.remove_data_btn)
        assets_layout.addLayout(icon_layout); assets_layout.addWidget(QLabel("Incluir:")); assets_layout.addWidget(self.data_list); assets_layout.addLayout(data_btns)
        layout.addWidget(io_group); layout.addWidget(opts_group); layout.addWidget(assets_group); layout.addStretch(); return frame
    def _create_right_column(self):
        frame = QFrame(); layout = QVBoxLayout(frame); console_group = QGroupBox("Consola de Salida"); console_layout = QVBoxLayout(console_group); self.log_console = QPlainTextEdit(); self.log_console.setReadOnly(True); console_layout.addWidget(self.log_console); layout.addWidget(console_group, 1)
        actions_layout = QHBoxLayout(); self.progress_bar = QProgressBar(); self.progress_bar.setRange(0,0); self.progress_bar.setVisible(False)
        self.open_folder_btn = QPushButton("Abrir Carpeta", icon=QIcon.fromTheme("folder")); self.open_folder_btn.setEnabled(False)
        self.build_btn = QPushButton("Iniciar Proceso", icon=QIcon.fromTheme("system-run")); self.build_btn.setProperty("class", "special")
        self.cancel_btn = QPushButton("Cancelar", icon=QIcon.fromTheme("process-stop")); self.cancel_btn.setStyleSheet("background-color: #BF360C;")
        self.action_stack = QStackedWidget(); self.action_stack.addWidget(self.build_btn); self.action_stack.addWidget(self.cancel_btn)
        actions_layout.addWidget(self.open_folder_btn); actions_layout.addStretch(); actions_layout.addWidget(self.progress_bar, 1); actions_layout.addSpacing(10); actions_layout.addWidget(self.action_stack)
        footer_frame = QFrame(); footer_layout = QHBoxLayout(footer_frame)
        self.save_config_btn = QPushButton("Guardar", icon=QIcon.fromTheme("document-save")); self.load_config_btn = QPushButton("Cargar", icon=QIcon.fromTheme("document-open"))
        footer_layout.addStretch(); footer_layout.addWidget(self.load_config_btn); footer_layout.addWidget(self.save_config_btn)
        layout.addLayout(actions_layout); layout.addWidget(footer_frame); return frame
    def _connect_signals(self):
        self.script_btn.clicked.connect(self._select_script); self.output_dir_btn.clicked.connect(self._select_output_dir); self.icon_btn.clicked.connect(self._select_icon)
        self.add_file_btn.clicked.connect(self._add_data_file); self.add_folder_btn.clicked.connect(self._add_data_folder); self.remove_data_btn.clicked.connect(self._remove_data_item)
        self.build_btn.clicked.connect(self._start_build); self.cancel_btn.clicked.connect(self._cancel_build); self.open_folder_btn.clicked.connect(self._open_output_folder)
        self.save_config_btn.clicked.connect(self._save_config); self.load_config_btn.clicked.connect(self._load_config)
    def _start_build(self):
        builder_options = self._get_builder_options(); script_to_build = builder_options["script_path"]; output_dir = builder_options["output_dir"]
        if not all([script_to_build, output_dir, Path(script_to_build).exists(), Path(output_dir).is_dir()]):
            QMessageBox.critical(self, "Error", "Especifica un script y carpeta de salida válidos."); return
        self.log_console.clear(); self._set_ui_for_build(True)
        obfuscation_opts = self.obfuscation_widget.get_options()
        if obfuscation_opts["enabled"]:
            self._log(f"Fase 1: Ofuscando con {obfuscation_opts['engine']}...", "info")
            try: script_to_build = run_obfuscator(script_to_build, output_dir, obfuscation_opts)
            except Exception as e: self._build_finished(-1, error=e); return
            self._log("Ofuscación completada.", "success")
        self._log("Fase 2: Empaquetando con PyInstaller...", "info")
        builder_options["script_path"] = script_to_build; command = build_pyinstaller_command(builder_options)
        self.thread = BuilderThread(command); self.thread.log_message.connect(self._log); self.thread.finished.connect(lambda code: self._build_finished(code)); self.thread.start()
    def _build_finished(self, return_code, error=None):
        self._set_ui_for_build(False); output_dir = self.output_dir_edit.text()
        for temp in ["temp_ast_build", "temp_pyarmor_build"]:
            temp_path = os.path.join(output_dir, temp)
            if os.path.exists(temp_path): shutil.rmtree(temp_path, ignore_errors=True)
        if error or return_code != 0:
            msg = f"Error en el proceso: {error}" if error else f"El proceso falló con código {return_code}"
            self._log(f"\nPROCESO FALLIDO: {msg} ❌", "error"); QMessageBox.critical(self, "Fallo", msg)
        else: self._log("\n¡Proceso completo! ✔️", "success"); QMessageBox.information(self, "Éxito", "Proceso finalizado correctamente.")
    def _cancel_build(self):
        if self.thread and self.thread.isRunning(): self.thread.stop(); self.action_stack.setEnabled(False)
    def _set_ui_for_build(self, building):
        self.action_stack.setCurrentIndex(1 if building else 0); self.action_stack.setEnabled(True)
        dist_dir = os.path.join(self.output_dir_edit.text(), 'dist')
        self.open_folder_btn.setEnabled(not building and dist_dir and Path(dist_dir).exists()); self.progress_bar.setVisible(building)
        for i in range(self.tabs.count()): self.tabs.setTabEnabled(i, not building)
    def _get_builder_options(self): return {"script_path":self.script_edit.text(),"output_dir":self.output_dir_edit.text(),"exe_name":self.exe_name_edit.text(),"one_file":self.one_file_check.isChecked(),"no_console":self.no_console_check.isChecked(),"clean":self.clean_check.isChecked(),"icon_path":self.icon_edit.text(),"data_files":[self.data_list.item(i).text() for i in range(self.data_list.count())]}
    def _select_script(self):
        path,_=QFileDialog.getOpenFileName(self,"Seleccionar","", "*.py;*.pyw");
        if path: self.script_edit.setText(path);self._update_defaults(path)
    def _update_defaults(self,path):
        if not self.exe_name_edit.text():self.exe_name_edit.setText(Path(path).stem)
        if not self.output_dir_edit.text():self.output_dir_edit.setText(str(Path(path).parent))
    def _select_output_dir(self):path=QFileDialog.getExistingDirectory(self,"Seleccionar");_select_output_dir
    def _select_icon(self):path,_=QFileDialog.getOpenFileName(self,"Seleccionar","", "*.ico");_select_icon
    def _add_data_file(self):path,_=QFileDialog.getOpenFileName(self,"Seleccionar");_add_data_file
    def _add_data_folder(self):path=QFileDialog.getExistingDirectory(self,"Seleccionar");_add_data_folder
    def _remove_data_item(self):
        for item in self.data_list.selectedItems():self.data_list.takeItem(self.data_list.row(item))
    def _log(self,msg,level="info"):
        cursor=self.log_console.textCursor();cursor.movePosition(QTextCursor.MoveOperation.End);fmt=QTextCharFormat();
        if level=="error":fmt.setForeground(QColor("#E53935"))
        elif level=="success":fmt.setForeground(QColor("#7CB342"));fmt.setFontWeight(QFont.Bold)
        elif level=="command":fmt.setForeground(QColor("#42A5F5"));fmt.setFontItalic(True)
        else:fmt.setForeground(self.palette().color(QPalette.WindowText))
        cursor.mergeCharFormat(fmt);cursor.insertText(msg + "\n");self.log_console.ensureCursorVisible()
    def _open_output_folder(self):
        dist_dir = os.path.join(self.output_dir_edit.text(),'dist');
        if dist_dir and Path(dist_dir).exists(): os.startfile(dist_dir) if sys.platform=="win32" else subprocess.call(["open",dist_dir])
        else: QMessageBox.warning(self,"No Encontrado","La carpeta de salida 'dist' no existe.")
    def _save_config(self):
        path,_=QFileDialog.getSaveFileName(self,"Guardar","", "*.pbc.json");
        if not path:return
        config=self._get_builder_options();config.update(self.obfuscation_widget.get_options());
        try:
            with open(path,'w') as f:json.dump(config,f,indent=4)
            self.statusBar().showMessage("Configuración guardada",3000)
        except Exception as e:QMessageBox.critical(self,"Error",f"{e}")
    def _load_config(self):
        path,_=QFileDialog.getOpenFileName(self,"Cargar","", "*.pbc.json");
        if not path:return
        try:
            with open(path,'r') as f:config=json.load(f)
            self.script_edit.setText(config.get("script_path",""));self.output_dir_edit.setText(config.get("output_dir",""));self.exe_name_edit.setText(config.get("exe_name",""))
            self.one_file_check.setChecked(config.get("one_file",True));self.no_console_check.setChecked(config.get("no_console",True));self.clean_check.setChecked(config.get("clean",False))
            self.icon_edit.setText(config.get("icon_path",""));self.data_list.clear()
            for item in config.get("data_files",[]):self.data_list.addItem(item)
            self.obfuscation_widget.enable_check.setChecked(config.get("enabled",False))
            self.statusBar().showMessage("Configuración cargada",3000)
        except Exception as e:QMessageBox.critical(self,"Error",f"{e}")
    def closeEvent(self,event):
        if self.thread and self.thread.isRunning():self.thread.stop();self.thread.wait()
        event.accept()