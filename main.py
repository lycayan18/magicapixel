import sys

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from canvas import Canvas


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas(32, 32)

        self.initUI()

    def initUI(self):
        pointer = QtGui.QCursor()
        pointer.setShape(Qt.CursorShape.PointingHandCursor)

        self.setGeometry(500, 500, 640, 480)
        self.setWindowTitle("Magica Pixel")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    widget.show()

    sys.exit(app.exec())
