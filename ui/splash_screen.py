import time
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QLinearGradient

class LoadingThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal()

    def run(self):
        # Mensajes que irán cambiando
        messages = [
            "Authenticating environment...",
            "Loading security modules...",
            "Initializing UI engine...",
            "Verifying assets...",
            "Starting PY-BUILDER..."
        ]
        
        # Animación suave de 0 a 100
        for i in range(101):
            time.sleep(0.03) # 30ms por paso = ~3 segundos total
            self.progress.emit(i)
            
            # Cambiar mensaje según el porcentaje
            if i < 20: self.status.emit(messages[0])
            elif i < 40: self.status.emit(messages[1])
            elif i < 60: self.status.emit(messages[2])
            elif i < 80: self.status.emit(messages[3])
            else: self.status.emit(messages[4])
            
        time.sleep(0.5)
        self.finished.emit()

class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 350)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.font_title = QFont("Segoe UI", 32, QFont.Bold)
        self.font_sub = QFont("Consolas", 10)
        self.progress_val = 0
        self.status_msg = "Initializing..."
        
        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_progress(self, val):
        self.progress_val = val
        self.repaint() # Forzar repintado inmediato

    def update_status(self, msg):
        self.status_msg = msg
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # 1. Fondo Negro Solido
        painter.setBrush(QColor(10, 10, 10))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 15, 15)

        # 2. Borde Fino
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(1,1,-1,-1), 15, 15)

        # 3. Título
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(self.font_title)
        painter.drawText(rect.adjusted(0, -50, 0, 0), Qt.AlignCenter, "PY-BUILDER")

        # 4. Subtítulo
        painter.setPen(QColor(0, 188, 212)) # Cyan
        painter.setFont(self.font_sub)
        painter.drawText(rect.adjusted(0, 20, 0, 0), Qt.AlignCenter, "// STUDIO EDITION v2.0 //")

        # 5. Barra de Progreso (Fondo)
        bar_w = 400
        bar_h = 6
        bar_x = (rect.width() - bar_w) // 2
        bar_y = 250
        
        painter.setBrush(QColor(30, 30, 30))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        # 6. Barra de Progreso (Relleno Animado)
        # Usamos Cyan brillante para que se vea bien
        fill_w = int(bar_w * (self.progress_val / 100))
        painter.setBrush(QColor(0, 255, 255)) # Cyan Neon
        painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)

        # 7. Texto de Estado
        painter.setPen(QColor(150, 150, 150))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(rect.adjusted(0, 140, 0, 0), Qt.AlignCenter, self.status_msg)