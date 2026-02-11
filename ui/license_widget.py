# ui/license_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class LicenseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(15)

        # --- CARD 1 ---
        self.card_info = QFrame()
        self.card_info.setProperty("class", "Card")
        self.card_info.enable_shadow = lambda enabled, color=QColor(0,0,0,20): self._set_shadow(self.card_info, enabled, color)
        
        l1 = QVBoxLayout(self.card_info)
        l1.setContentsMargins(20, 20, 20, 20)
        l1.addWidget(QLabel("LICENSE & COPYRIGHT", objectName="Header"))
        desc = QLabel("<b>Py-Builder Studio Pro</b><br>Version 2.1.0<br><br>© Todos los derechos reservados.")
        desc.setWordWrap(True)
        l1.addWidget(desc)

        # --- CARD 2 ---
        self.card_credits = QFrame()
        self.card_credits.setProperty("class", "Card")
        self.card_credits.enable_shadow = lambda enabled, color=QColor(0,0,0,20): self._set_shadow(self.card_credits, enabled, color)
        
        l2 = QVBoxLayout(self.card_credits)
        l2.setContentsMargins(20, 20, 20, 20)
        l2.setSpacing(15)
        l2.addWidget(QLabel("SPECIAL CREDITS", objectName="Header"))
        l2.addWidget(QLabel("Desarrollado y protegido por:"))

        # 🔥 NOMBRES CON COLOR BLANCO FORZADO INICIAL 🔥
        self.lbl_daniel = QLabel("DANIEL MERA")
        self.lbl_gabriela = QLabel("GABRIELA INTRIAGO")
        
        style_init = "font-size: 18px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;"
        self.lbl_daniel.setStyleSheet(style_init)
        self.lbl_gabriela.setStyleSheet(style_init)

        l2.addWidget(self.lbl_daniel)
        l2.addWidget(self.lbl_gabriela)
        l2.addWidget(QLabel("SYSTEM PROTECTED BY ARACHNID ENGINE", styleSheet="color: #555; font-size: 10px;"))

        layout.addWidget(self.card_info); layout.addWidget(self.card_credits); layout.addStretch()

    def _set_shadow(self, target, enabled, color):
        if enabled:
            sh = QGraphicsDropShadowEffect(target); sh.setBlurRadius(20); sh.setColor(color)
            target.setGraphicsEffect(sh)
        else: target.setGraphicsEffect(None)

    def update_theme_style(self, theme):
        accent = "#3B82F6" if theme == "LUMINA" else "#FFFFFF"
        style = f"font-size: 18px; font-weight: 900; color: {accent}; letter-spacing: 1px;"
        self.lbl_daniel.setStyleSheet(style); self.lbl_gabriela.setStyleSheet(style)