import sys
import random
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsPolygonItem,
    QFrame,
)
from PySide6.QtGui import QPolygonF, QColor, QBrush, QPainter, QFont, QPen
from PySide6.QtCore import QPointF, Qt, QTimer

from perx.ctypes import *

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 500

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600


class TimeRuler(QWidget):
    """Custom vertical time ruler (0–1 s)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(80)
        self.setMinimumHeight(CANVAS_HEIGHT)
        self.ticks = [
            ("1 s", 1.0),
            ("500 ms", 0.500),
            ("100 ms", 0.100),
            ("10 ms", 0.010),
            ("", 0.0),
        ]
        self.fill_time = 0.150  # time in seconds to fill (150 ms)

    def set_fill_time(self, t_sec: float):
        """Update the filled time and repaint."""
        self.fill_time = t_sec
        self.update()  # trigger repaint


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)

        margin_top = 20
        margin_bottom = 20
        height = self.height() - margin_top - margin_bottom
        x = 20  # position of the spine line

        # Draw filled portion (green)
        y_fill = margin_top + height - self.fill_time * height
        painter.fillRect(
            x - 8,
            y_fill,
            16,
            height - (y_fill - margin_top),
            QColor(100, 200, 100, 180),
        )

        # Draw spine
        painter.drawLine(x, margin_top, x, margin_top + height)

        # Draw ticks and labels
        for label, t in self.ticks:
            y = margin_top + height - t * height

            # Special style for t = 0.01
            if t == 0.01:
            # if label == "10 ms":
                font = QFont()
                font.setPointSize(12)  # bigger
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(QColor(255, 0, 0))  # red
            else:
                font = QFont()
                font.setPointSize(9)
                painter.setFont(font)
                painter.setPen(QColor(0, 0, 0))  # black

            painter.drawLine(x - 8, y, x + 8, y)
            painter.drawText(x + 12, y + 4, label)

        # Title
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(x - 18, 15, "Inference time")


class ShapeSpawner(QWidget):
    def __init__(self):
        super().__init__()

        self.server_state = {"visual-servo": 0, "efnet": 0, "tbert": 0}

        self.setWindowTitle("Shape Spawner")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # FIXED SIZE


        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        canvas_layout = QHBoxLayout()  # canvas + ruler side by side

        # Buttons
        self.btn_circle = QPushButton("visual-servo")
        self.btn_square = QPushButton("tbert")
        self.btn_pentagon = QPushButton("efnet")
        self.btn_clear = QPushButton("CLEAR")

        button_layout.addWidget(self.btn_circle)
        button_layout.addWidget(self.btn_square)
        button_layout.addWidget(self.btn_pentagon)
        button_layout.addWidget(self.btn_clear)

        # Canvas
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(CANVAS_WIDTH, CANVAS_HEIGHT)

        # Ruler widget
        self.ruler = TimeRuler()
        self.ruler.set_fill_time(0.150)

        # Add canvas and ruler side by side
        canvas_layout.addWidget(self.view)
        canvas_layout.addWidget(self.ruler)

        # Connect buttons
        self.btn_circle.clicked.connect(self.spawn_circle)
        self.btn_square.clicked.connect(self.spawn_square)
        self.btn_pentagon.clicked.connect(self.spawn_pentagon)
        self.btn_clear.clicked.connect(self.clear_canvas)

        # Assemble layouts
        main_layout.addLayout(button_layout)
        main_layout.addLayout(canvas_layout)
        self.setLayout(main_layout)

        # Gravity timer
        self.gravity_timer = QTimer()
        self.gravity_timer.timeout.connect(self.apply_gravity)
        self.gravity_timer.start(5)

    def apply_gravity(self, bottom_padding=15):
        for item in self.scene.items():
            if not getattr(item, "_falling", False):
                continue

            # move down
            item.moveBy(0, 3)

            # bottom check with padding
            bottom = self.view.height() - bottom_padding
            if item.y() + item.boundingRect().height() >= bottom:
                item.setY(bottom - item.boundingRect().height())
                item._falling = False
                continue

            # check collision
            for other in self.scene.items():
                if other is item:
                    continue
                if item.collidesWithItem(other):
                    item.setY(other.y() - item.boundingRect().height())
                    item._falling = False
                    break

    def clear_canvas(self):
        self.scene.clear()
        for k in self.server_state.keys():
            self.server_state[k] = 0

    def spawn_circle(self):
        scale = APP_SCALES["visual-servo"]
        circle = QGraphicsEllipseItem(0, 0, 50 * scale, 50 * scale)
        circle.setBrush(QBrush(QColor("#ffffb3")))
        circle.setPen(Qt.NoPen)
        self.place_item_without_overlap(circle)
        circle.setRotation(random.uniform(0, 90))
        circle._falling = True
        self.scene.addItem(circle)
        self.inc_server_state("visual-servo")

    def spawn_square(self):
        scale = APP_SCALES["tbert"]
        square = QGraphicsRectItem(0, 0, 50 * scale, 50 * scale)
        square.setBrush(QBrush(QColor("#fccde5")))
        square.setPen(Qt.NoPen)
        self.place_item_without_overlap(square)
        square.setRotation(random.uniform(0, 90))
        square._falling = True
        self.scene.addItem(square)
        self.inc_server_state("tbert")

    def spawn_pentagon(self):
        scale = APP_SCALES["iclf-efnet"]
        polygon = QPolygonF(
            [
                QPointF(25 * scale, 0 * scale),
                QPointF(50 * scale, 20 * scale),
                QPointF(40 * scale, 50 * scale),
                QPointF(10 * scale, 50 * scale),
                QPointF(0 * scale, 20 * scale),
            ]
        )
        pentagon = QGraphicsPolygonItem(polygon)
        pentagon.setBrush(QBrush(QColor("#b3de69")))
        pentagon.setPen(Qt.NoPen)
        self.place_item_without_overlap(pentagon)
        pentagon.setRotation(random.uniform(0, 90))
        pentagon._falling = True
        self.scene.addItem(pentagon)
        self.inc_server_state("efnet")

    def place_item_without_overlap(self, item, max_attempts=100, padding=10):
        """
        Place item at the top with random X, avoiding overlap.
        padding: space around edges (left, right, bottom)
        """
        for _ in range(max_attempts):
            x = random.randint(
                padding, int(CANVAS_WIDTH - item.boundingRect().width() - padding)
            )
            y = padding  # spawn a bit below the top
            item.setPos(x, y)
            self.scene.addItem(item)
            if not item.collidingItems():
                return True
            self.scene.removeItem(item)
        return False

    def inc_server_state(self, app_name):
        self.server_state[app_name] += 1
        print(self.server_state)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShapeSpawner()
    window.show()
    sys.exit(app.exec())
