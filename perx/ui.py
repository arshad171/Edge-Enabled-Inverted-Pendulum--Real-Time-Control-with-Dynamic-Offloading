import sys
import random
import time
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
    QLabel
)
from PySide6.QtGui import QPolygonF, QColor, QBrush, QPainter, QFont, QPen, QPalette
from PySide6.QtCore import QPointF, Qt, QTimer

from perx.ctypes import *

CANVAS_WIDTH = 750
CANVAS_HEIGHT = 500

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 800


class HorizontalRuler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.MAX_TICK = 32
        self.setFixedHeight(50)
        self.setMinimumWidth(CANVAS_WIDTH)
        self.ticks = [
            ("0", 0.0),
            ("16 GB", 16 / self.MAX_TICK),
            ("24 GB", 24 / self.MAX_TICK),
            ("32 GB", 1.0),
        ]

        self.fill_value = 18

    def set_set_fill_value(self, value: float):
        """Update the filled time and repaint."""
        self.fill_value = value
        self.update()  # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)

        margin_left = 20
        margin_right = 30
        width = self.width() - margin_left - margin_right
        y = 20  # horizontal axis line

        # Draw spine
        painter.drawLine(margin_left, y, margin_left + width, y)

        # Draw ticks and labels
        for label, t in self.ticks:
            x = margin_left + t * width

            if t == 32 / self.MAX_TICK:
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

            painter.drawLine(x, y - 8, x, y + 8)
            painter.drawText(x - 10, y + 25, label)

        fill_ratio = min(1.0, self.fill_value / self.MAX_TICK)
        fill_width = int(fill_ratio * width)
        # color = QColor(100, 75, 200, 180)
        color = QColor(25, 25, 25, 180)

        painter.fillRect(
            margin_left,
            y - 8,
            fill_width,
            16,  # thickness of the bar
            color,
        )

        # Title
        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        painter.setPen(QColor(0, 0, 0))  # red
        painter.setFont(font)
        painter.drawText(width // 2, 10, "Memory")

class TimeRuler(QWidget):
    """Custom vertical time ruler (0–1 s)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(80)
        self.setMinimumHeight(CANVAS_HEIGHT)
        self.MAX_TICK = 500
        self.ticks = [
            ("500 ms", 1.0),
            ("300 ms", 300 / self.MAX_TICK),
            ("200 ms", 200 / self.MAX_TICK),
            ("120 ms", 120 / self.MAX_TICK),
            ("0 ", 0.0),
        ]
        self.fill_time = 120 / self.MAX_TICK
        self.color = "green"

    def set_set_fill_value(self, value: float):
        """Update the filled time and repaint."""
        self.fill_time = value
        self.update()  # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)

        margin_top = 30
        margin_bottom = 30
        height = self.height() - margin_top - margin_bottom
        x = 20  # position of the spine line

        # Draw filled portion (green)
        y_fill = margin_top + height - self.fill_time * 1000 / self.MAX_TICK * height

        if self.fill_time <= 0.12:
            color = QColor(100, 200, 100, 180)
        elif self.fill_time > 0.12 and self.fill_time < 0.3:
            color = QColor(255, 255, 0, 180)
        elif self.fill_time > 0.3:
            color = QColor(255, 0, 0, 180)

        painter.fillRect(
            x - 8,
            y_fill,
            16,
            height - (y_fill - margin_top),
            color,
        )

        # Draw spine
        painter.drawLine(x, margin_top, x, margin_top + height)

        # Draw ticks and labels
        for label, t in self.ticks:
            y = margin_top + height - t * height

            # Special style for t = 0.01
            if t == 120 / self.MAX_TICK:
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

        self.revenue = 0.0
        self.server_state = {"visual-servo": 0, "iclf-efnet": 0, "text-tbert": 0}

        self.setWindowTitle("PERX")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)  # FIXED SIZE

        # Layouts
        main_layout = QVBoxLayout()
        deploy_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        canvas_layout = QHBoxLayout()  # canvas + ruler side by side

        title_label = QLabel("Beat PERX")
        font = QFont()
        font.setPointSize(28)  # larger font size
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet("color: red;")  # set text color to red
        title_label.setAlignment(Qt.AlignCenter)  # center horizontally

        self.score_label = QLabel(f"$$ {self.revenue}")
        font = QFont()
        font.setPointSize(20)  # larger font size
        font.setBold(True)
        self.score_label.setFont(font)
        self.score_label.setStyleSheet("color: white;")  # set text color to red
        self.score_label.setAlignment(Qt.AlignRight)  # center horizontally

        # Buttons
        self.btn_circle = QPushButton("visual-servo")
        self.btn_circle.setStyleSheet(
            """
            QPushButton {
                background-color: #ffffb3;
                color: black;
                border-style: outset;
                border-width: 1px;
                border-radius: 6px;
                border-color: beige;
                font: bold 12px;
                min-width: 10em;
                padding: 3px;
            }
            """
        )

        self.btn_square = QPushButton("text-tbert")
        self.btn_square.setStyleSheet(
            """
            QPushButton {
                background-color: #fccde5;
                color: black;
                border-style: outset;
                border-width: 1px;
                border-radius: 6px;
                border-color: beige;
                font: bold 12px;
                min-width: 10em;
                padding: 3px;
            }
            """
        )

        self.btn_pentagon = QPushButton("iclf-efnet")
        self.btn_pentagon.setStyleSheet(
            """
            QPushButton {
                background-color: #b3de69;
                color: black;
                border-style: outset;
                border-width: 1px;
                border-radius: 6px;
                border-color: beige;
                font: bold 12px;
                min-width: 10em;
                padding: 3px;
            }
            """
        )

        self.btn_clear = QPushButton("CLEAR")
        self.btn_rain = QPushButton("Make it rain!")
        self.btn_deploy = QPushButton("Deploy")

        deploy_layout.addStretch()
        deploy_layout.addWidget(self.btn_deploy)
        deploy_layout.addStretch()

        button_layout.addWidget(self.btn_circle)
        button_layout.addWidget(self.btn_square)
        button_layout.addWidget(self.btn_pentagon)
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_rain)

        # Canvas
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFixedSize(CANVAS_WIDTH, CANVAS_HEIGHT)

        # Ruler widget
        self.inf_time_ruler = TimeRuler()
        self.inf_time_ruler.set_set_fill_value(0.150)

        self.horiz_ruler = HorizontalRuler()

        # Add canvas and ruler side by side
        canvas_layout.addWidget(self.view)
        canvas_layout.addWidget(self.inf_time_ruler)

        # Connect buttons
        self.btn_circle.clicked.connect(self.spawn_circle)
        self.btn_square.clicked.connect(self.spawn_square)
        self.btn_pentagon.clicked.connect(self.spawn_pentagon)
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.btn_rain.clicked.connect(self.rain)

        # Assemble layouts
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.score_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(canvas_layout)
        main_layout.addWidget(self.horiz_ruler)
        main_layout.addLayout(deploy_layout)

        self.setLayout(main_layout)

        # Gravity timer
        self.gravity_timer = QTimer()
        self.gravity_timer.timeout.connect(self.apply_gravity)
        self.gravity_timer.start(5)

        self.add_visual_servos()

    def add_visual_servos(self):
        for _ in range(3):
            self.spawn_circle(hatch=True)

    def apply_gravity(self, bottom_padding=30):
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
        self.revenue = 0

        for k in self.server_state.keys():
            self.server_state[k] = 0

        self.add_visual_servos()

    def rain(self):
        self.clear_canvas()

        for _ in range(10):
            rnd = random.random()
            if rnd > 0 and rnd < 0.33:
                self.spawn_circle()
            elif rnd > 0.33 and rnd < 0.66:
                self.spawn_square()
            elif rnd > 0.66:
                self.spawn_pentagon()

            time.sleep(0.5)

    def spawn_circle(self, hatch=False):
        scale = APP_SCALES["visual-servo"]
        circle = QGraphicsEllipseItem(0, 0, 50 * scale, 50 * scale)
        if hatch:
            brush = QBrush(QColor("#ffffb3"), Qt.DiagCrossPattern)
            count = 1
        else:
            brush = QBrush(QColor("#ffffb3"))
            count = 1.2
        circle.setBrush(brush)
        circle.setPen(Qt.NoPen)
        self.place_item_without_overlap(circle)
        circle.setRotation(random.uniform(0, 90))
        circle._falling = True
        self.scene.addItem(circle)
        self.inc_server_state("visual-servo", count=count)

    def spawn_square(self):
        scale = APP_SCALES["text-tbert"]
        square = QGraphicsRectItem(0, 0, 50 * scale, 50 * scale)
        square.setBrush(QBrush(QColor("#fccde5")))
        square.setPen(Qt.NoPen)
        self.place_item_without_overlap(square)
        square.setRotation(random.uniform(0, 90))
        square._falling = True
        self.scene.addItem(square)
        self.inc_server_state("text-tbert")

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
        self.inc_server_state("iclf-efnet")

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

    def inc_server_state(self, app_name, count=1):
        self.server_state[app_name] += count
        print(self.server_state)

        used_cap = 0.0
        self.revenue = 0
        for app, num_instances in self.server_state.items():
            used_cap += num_instances * APP_MEMS[app] * 1.5
            self.revenue += APP_REVS[app] * num_instances

        self.horiz_ruler.set_set_fill_value(used_cap)

        print(self.revenue)
        self.score_label.setText(f"$$ {self.revenue:.1f}")
        self.score_label.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShapeSpawner()
    window.show()
    sys.exit(app.exec())
