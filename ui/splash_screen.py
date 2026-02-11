import time
import math
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush
import time
import math
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

# ==========================================
# LÓGICA DE LA ARAÑA (Procedimental)
# ==========================================
class SpiderLeg:
    def __init__(self, angle_deg, length, spread):
        self.angle = math.radians(angle_deg)
        self.length = length
        self.spread = spread
        self.root = QPointF(0, 0)
        self.knee = QPointF(0, 0)
        self.foot = QPointF(0, 0)
        fx = math.cos(self.angle) * self.spread
        fy = math.sin(self.angle) * self.spread
        self.base_foot_pos = QPointF(fx, fy)

    def update(self, body_x, body_y, breathe_offset):
        body_radius = 15
        rx = body_x + math.cos(self.angle) * body_radius
        ry = body_y + math.sin(self.angle) * body_radius
        self.root = QPointF(rx, ry)
        self.foot = self.base_foot_pos
        mid_x = (self.root.x() + self.foot.x()) / 2
        mid_y = (self.root.y() + self.foot.y()) / 2
        dist = math.sqrt((self.root.x() - self.foot.x())**2 + (self.root.y() - self.foot.y())**2)
        knee_height = 30 + breathe_offset
        dx = self.foot.x() - self.root.x()
        dy = self.foot.y() - self.root.y()
        if dist > 0:
            perp_x = -dy / dist
            perp_y = dx / dist
        else:
            perp_x, perp_y = 0, 0
        self.knee = QPointF(mid_x + perp_x * 10, mid_y + perp_y * 10 - knee_height)

class CyberSpider:
    def __init__(self):
        self.legs = []
        self.legs.append(SpiderLeg(300, 50, 90)); self.legs.append(SpiderLeg(330, 60, 100))
        self.legs.append(SpiderLeg(30, 60, 100)); self.legs.append(SpiderLeg(60, 50, 90))
        self.legs.append(SpiderLeg(240, 50, 90)); self.legs.append(SpiderLeg(210, 60, 100))
        self.legs.append(SpiderLeg(150, 60, 100)); self.legs.append(SpiderLeg(120, 50, 90))
        self.body_x = 0; self.body_y = 0; self.target_x = 0; self.target_y = 0; self.time_counter = 0

    def set_target(self, tx, ty):
        limit = 40
        dist = math.sqrt(tx**2 + ty**2)
        if dist > limit:
            ratio = limit / dist
            tx *= ratio; ty *= ratio
        self.target_x = tx; self.target_y = ty

    def update(self):
        self.body_x += (self.target_x - self.body_x) * 0.1
        self.body_y += (self.target_y - self.body_y) * 0.1
        self.time_counter += 0.1
        breathe = math.sin(self.time_counter) * 2
        for leg in self.legs: leg.update(self.body_x, self.body_y, breathe)

class LoadingThread(QThread):
    progress = Signal(int); status = Signal(str); finished = Signal()
    def run(self):
        messages = ["NEURAL LINK ESTABLISHED...", "INJECTING PAYLOAD...", "BYPASSING SECURITY...", "COMPILING ASSETS...", "SYSTEM READY."]
        for i in range(101):
            time.sleep(0.04); self.progress.emit(i)
            if i < 20: self.status.emit(messages[0])
            elif i < 40: self.status.emit(messages[1])
            elif i < 60: self.status.emit(messages[2])
            elif i < 80: self.status.emit(messages[3])
            else: self.status.emit(messages[4])
        time.sleep(0.3); self.finished.emit()

# ==========================================
# SPLASH SCREEN INTERACTIVO
# ==========================================
class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 420)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.font_title = QFont("Segoe UI", 28, QFont.Bold)
        self.font_sub = QFont("Consolas", 9)
        self.font_status = QFont("Consolas", 8)
        self.progress_val = 0; self.status_msg = "INIT..."
        self.spider = CyberSpider()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    # 🔥 BLOQUEO DE CLIC AQUÍ 🔥
    def mousePressEvent(self, event):
        # Ignoramos el clic para que no se cierre solo
        pass

    def mouseMoveEvent(self, event):
        center_x = self.width() / 2
        center_y = (self.height() / 2) - 20 
        dx = event.position().x() - center_x
        dy = event.position().y() - center_y
        self.spider.set_target(dx, dy)

    def animate(self):
        self.spider.update()
        self.repaint()

    def update_progress(self, val): self.progress_val = val
    def update_status(self, msg): self.status_msg = msg

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        w = rect.width(); h = rect.height()
        center_x = w / 2; center_y = (h / 2) - 30

        painter.setBrush(QColor(5, 5, 5)); painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRect(rect)

        painter.translate(center_x, center_y)
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        for leg in self.spider.legs:
            painter.drawLine(leg.root, leg.knee); painter.drawLine(leg.knee, leg.foot)
            painter.drawEllipse(leg.root, 3, 3); painter.drawEllipse(leg.knee, 3, 3)
            painter.setBrush(QColor(255, 255, 255)); painter.drawEllipse(leg.foot, 2, 2)
            painter.setBrush(Qt.NoBrush)

        painter.setPen(QPen(QColor(255, 255, 255), 2)); painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(QRectF(self.spider.body_x - 12, self.spider.body_y - 15, 24, 30))
        painter.setBrush(QColor(255, 255, 255)); painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(self.spider.body_x - 5, self.spider.body_y - 5), 2, 2)
        painter.drawEllipse(QPointF(self.spider.body_x + 5, self.spider.body_y - 5), 2, 2)
        painter.translate(-center_x, -center_y)

        painter.setPen(QColor(255, 255, 255)); painter.setFont(self.font_title)
        painter.drawText(QRectF(0, 40, w, 50), Qt.AlignCenter, "PY-BUILDER")
        painter.setPen(QColor(180, 180, 180)); painter.setFont(self.font_sub)
        painter.drawText(QRectF(0, 85, w, 30), Qt.AlignCenter, "STUDIO // ARACHNID ENGINE")

        painter.fillRect(0, h-3, w, 3, QColor(20, 20, 20))
        painter.fillRect(0, h-3, int(w * (self.progress_val / 100)), 3, QColor(255, 255, 255))
        painter.setPen(QColor(150, 150, 150)); painter.setFont(self.font_status)
        painter.drawText(QRectF(20, h - 35, 300, 20), Qt.AlignLeft, f"> {self.status_msg}")
        painter.setPen(QColor(255, 255, 255)); painter.drawText(QRectF(w - 70, h - 35, 50, 20), Qt.AlignRight, f"{self.progress_val}%")