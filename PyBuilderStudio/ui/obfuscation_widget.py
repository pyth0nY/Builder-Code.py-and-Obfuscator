# Contenido COMPLETO Y CORREGIDO FINAL para: ui/obfuscation_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox, QLabel, 
    QComboBox, QStackedWidget, QFormLayout, QSpinBox,
    QHBoxLayout
)
from PySide6.QtCore import Signal


class ObfuscationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 15, 10, 15)
        
        obfuscation_group = QGroupBox("Seguridad y Ofuscación")
        group_layout = QVBoxLayout(obfuscation_group)
        
        self.enable_check = QCheckBox("Habilitar Ofuscación antes del empaquetado")
        group_layout.addWidget(self.enable_check)
        
        self.options_container = QWidget()
        container_layout = QVBoxLayout(self.options_container)
        container_layout.setContentsMargins(15, 10, 0, 0)
        
        form_layout = QFormLayout()
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["PyArmor (Ofuscación de Bytecode)", "PyFuscator (Ofuscación AST)"])
        form_layout.addRow("Motor de Ofuscación:", self.engine_combo)
        
        self.engine_options_stack = QStackedWidget()
        self.pyarmor_options_widget = self._create_pyarmor_options()
        self.pyfuscator_options_widget = self._create_pyfuscator_options()
        self.engine_options_stack.addWidget(self.pyarmor_options_widget)
        self.engine_options_stack.addWidget(self.pyfuscator_options_widget)
        
        container_layout.addLayout(form_layout)
        container_layout.addWidget(self.engine_options_stack)
        
        group_layout.addWidget(self.options_container)
        
        main_layout.addWidget(obfuscation_group)
        main_layout.addStretch()  # <--- ESTA LÍNEA ES IMPORTANTE PARA LA ESTÉTICA

        # --- Conexiones ---
        self.enable_check.toggled.connect(self.options_container.setVisible)
        self.engine_combo.currentIndexChanged.connect(self.engine_options_stack.setCurrentIndex)
        
        # --- Lógica de Estado Inicial ---
        self.options_container.setVisible(False)
        self.engine_options_stack.setCurrentIndex(self.engine_combo.currentIndex()) # <-- ¡¡LA LÍNEA QUE FALTABA!!

    def _create_pyarmor_options(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        obf_group = QGroupBox("Opciones de Ofuscación de Código")
        obf_layout = QFormLayout(obf_group)
        self.pyarmor_obf_code = QComboBox()
        self.pyarmor_obf_code.addItems(["2 - aplanado (muy seguro)", "1 - por defecto (seguro y rápido)", "0 - transparente (sin ofuscación)"])
        self.pyarmor_obf_code.setCurrentIndex(0)
        self.pyarmor_obf_code.setToolTip("Nivel de ofuscación para el bytecode del código.\n2 es el más alto, 1 es el estándar.")
        obf_layout.addRow("--obf-code:", self.pyarmor_obf_code)
        
        mod_group = QGroupBox("Opciones de Ofuscación de Módulos")
        mod_layout = QFormLayout(mod_group)
        self.pyarmor_obf_mod = QComboBox()
        self.pyarmor_obf_mod.addItems(["2 - ofuscación profunda", "1 - por defecto (recomendado)", "0 - descriptivo"])
        self.pyarmor_obf_mod.setToolTip("Cómo se ofuscan los nombres de los módulos dentro del paquete.")
        mod_layout.addRow("--obf-mod:", self.pyarmor_obf_mod)

        lic_group = QGroupBox("Restricciones (Licencia)")
        lic_layout = QVBoxLayout(lic_group)
        self.pyarmor_restrict_check = QCheckBox("Añadir Restricciones de Licencia")
        self.pyarmor_restrict_check.setToolTip("Embebe una licencia en el script que restringe su uso.")
        lic_options_widget = QWidget()
        lic_options_layout = QVBoxLayout(lic_options_widget)
        lic_options_layout.setContentsMargins(15, 5, 0, 0)
        self.pyarmor_platform_check = QCheckBox("Limitar a la plataforma actual (Windows/Linux/macOS)")
        self.pyarmor_platform_check.setToolTip("El ejecutable solo funcionará en el sistema operativo donde fue compilado.")
        lic_options_layout.addWidget(self.pyarmor_platform_check)
        lic_options_widget.setVisible(False)
        self.pyarmor_restrict_check.toggled.connect(lic_options_widget.setVisible)
        lic_layout.addWidget(self.pyarmor_restrict_check)
        lic_layout.addWidget(lic_options_widget)

        layout.addWidget(obf_group)
        layout.addWidget(mod_group)
        layout.addWidget(lic_group)
        layout.addStretch()
        return widget
        
    def _create_pyfuscator_options(self):
        # ... (Este método estaba bien, no necesita cambios)
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 10, 0, 0)
        basic_group = QGroupBox("Opciones Básicas"); basic_layout = QVBoxLayout(basic_group)
        self.ast_obfuscate_strings = QCheckBox("Ofuscar strings (texto)"); self.ast_obfuscate_strings.setChecked(True)
        self.ast_obfuscate_numbers = QCheckBox("Ofuscar números"); self.ast_obfuscate_numbers.setChecked(True)
        self.ast_obfuscate_names = QCheckBox("Ofuscar nombres"); self.ast_obfuscate_names.setChecked(True)
        basic_layout.addWidget(self.ast_obfuscate_strings); basic_layout.addWidget(self.ast_obfuscate_numbers); basic_layout.addWidget(self.ast_obfuscate_names)
        advanced_group = QGroupBox("Técnicas Avanzadas"); advanced_layout = QVBoxLayout(advanced_group)
        self.ast_cff = QCheckBox("Aplanamiento del Flujo de Control (CFF)"); self.ast_cff.setChecked(True)
        self.ast_opaque_predicates = QCheckBox("Predicados Opacos"); self.ast_opaque_predicates.setChecked(True)
        self.ast_dead_code = QCheckBox("Inserción de Código Muerto"); self.ast_dead_code.setChecked(True)
        self.ast_string_encryption = QCheckBox("Cifrado Multi-capa de Strings"); self.ast_string_encryption.setChecked(True)
        advanced_layout.addWidget(self.ast_cff); advanced_layout.addWidget(self.ast_opaque_predicates); advanced_layout.addWidget(self.ast_dead_code); advanced_layout.addWidget(self.ast_string_encryption)
        level_layout = QHBoxLayout(); level_label = QLabel("Nivel de ofuscación (1-3):")
        self.ast_level = QSpinBox(); self.ast_level.setRange(1, 3); self.ast_level.setValue(2)
        level_layout.addWidget(level_label); level_layout.addWidget(self.ast_level); level_layout.addStretch()
        layout.addWidget(basic_group); layout.addWidget(advanced_group); layout.addLayout(level_layout)
        return widget

    def get_options(self) -> dict:
        # ... (Este método estaba bien, no necesita cambios)
        if not self.enable_check.isChecked(): return {"enabled": False}
        engine_map = {0: "pyarmor", 1: "pyfuscator"}; engine_idx = self.engine_combo.currentIndex()
        options = { "enabled": True, "engine": engine_map.get(engine_idx, "pyarmor") }
        if options["engine"] == "pyarmor":
            options.update({
                "pyarmor_obf_code": int(self.pyarmor_obf_code.currentText().split(" ")[0]),
                "pyarmor_obf_mod": int(self.pyarmor_obf_mod.currentText().split(" ")[0]),
                "pyarmor_add_restrict": self.pyarmor_restrict_check.isChecked(),
                "pyarmor_platform_specific": self.pyarmor_platform_check.isChecked(),
            })
        elif options["engine"] == "pyfuscator":
            options.update({
                'ast_obfuscate_strings': self.ast_obfuscate_strings.isChecked(),
                'ast_obfuscate_numbers': self.ast_obfuscate_numbers.isChecked(),
                'ast_obfuscate_names': self.ast_obfuscate_names.isChecked(),
                'ast_level': self.ast_level.value(),
                'ast_cff': self.ast_cff.isChecked(),
                'ast_opaque_predicates': self.ast_opaque_predicates.isChecked(),
                'ast_dead_code': self.ast_dead_code.isChecked(),
                'ast_string_encryption': self.ast_string_encryption.isChecked(),})
        return options