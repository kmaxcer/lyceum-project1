import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
import random


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Желтые окружности")
        self.setGeometry(100, 100, 400, 400)

        self.button = QPushButton("Построить окружности", self)
        self.button.setGeometry(150, 350, 150, 30)
        self.button.clicked.connect(self.draw_circles)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.yellow)

        for _ in range(1, 3):
            radius = random.randint(10, 100)
            x = 200 * _
            y = 100
            painter.drawEllipse(x, y, radius, radius)

    def draw_circles(self):
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
