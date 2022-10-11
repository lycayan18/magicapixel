import sys

from PyQt5.QtWidgets import QApplication, QPushButton, QWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF
from canvas import Canvas
from canvasview import CanvasView
from ui.mainwindow.mainwindow import Ui_MainWindow
from ui.styles.button import CURRENT_BRUSH_BUTTON_STYLESHEET


class MainWidget(Ui_MainWindow, QWidget):
    def __init__(self):
        super().__init__()
        # Current drawing size
        self.current_width = 32
        self.current_height = 32

        self.canvas = Canvas(self.current_width, self.current_height)

        # Canvas for previewing what you're going to draw
        self.preview_canvas = Canvas(self.current_width, self.current_height)

        self.canvas_view = CanvasView(
            self.current_width, self.current_height,
            self.preview_canvas,
            parent=self
        )

        self.current_color = (255, 255, 255, 255)

        # To handle mouse move without mouse click
        self.setMouseTracking(True)
        self.canvas_view.setMouseTracking(True)

        self.current_brush = "pen"  # pen, stroke, picker, fill

        self.mouse_state = {
            "pressed": False,
            "start_pos": QPoint(0, 0),
            "current_pos": QPoint(0, 0),
            "prev_pos": QPoint(0, 0)
        }

        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle("Magica Pixel")
        self.setWindowIcon(QtGui.QIcon("./assets/icon.ico"))

        self.canvas_view.setGeometry(0, 0, 800, 500)
        self.canvas_view.show()

        self.connect_brush_button_handler(self.penButton, "pen")
        self.connect_brush_button_handler(self.strokeButton, "stroke")
        self.connect_brush_button_handler(self.pickerButton, "picker")
        self.connect_brush_button_handler(self.fillButton, "fill")

    def connect_brush_button_handler(self, button: QPushButton, brush: str):
        button.clicked.connect(
            lambda: self.handle_brush_button_clicked(button, brush))

    def handle_brush_button_clicked(self, button: QPushButton, brush: str):
        # Reset stylesheet for all buttons
        self.penButton.setStyleSheet("")
        self.strokeButton.setStyleSheet("")
        self.pickerButton.setStyleSheet("")
        self.fillButton.setStyleSheet("")

        self.current_brush = brush

        button.setStyleSheet(CURRENT_BRUSH_BUTTON_STYLESHEET)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        self.canvas_view.setGeometry(QRect(QPoint(0, 0), ev.size()))

        self.brushPanel.move(0, ev.size().height() / 2 - 250)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_state["pressed"] = True
        self.mouse_state["start_pos"] = self.mouse_state["current_pos"]

        self.use_brush()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_state["pressed"] = False

        self.draw_to_canvas()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_state["prev_pos"] = self.mouse_state["current_pos"]
        self.mouse_state["current_pos"] = ev.pos()

        if self.mouse_state["pressed"]:
            self.use_brush()

    def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
        # Scale canvas
        shift = self.canvas_view.shift
        start_point = QPointF(
            shift.x() + self.width() * 0.5,
            shift.y() + self.height() * 0.5,
        )

        if ev.angleDelta().y() > 0:
            # Zoom in
            self.canvas_view.shift_by(
                (start_point - self.mouse_state["current_pos"]))
            self.canvas_view.scale_by(2)
        else:
            # Zoom out
            self.canvas_view.shift_by(
                (self.mouse_state["current_pos"] - start_point) * 0.5)
            self.canvas_view.scale_by(0.5)

        self.repaint()

    def use_brush(self):
        if self.current_brush == "pen":
            # To prevent "bubbles" we need to draw the line from mouse previous
            # position to mouse current position
            # Otherwise, you'll see "holes"
            self.canvas_view.draw_pixel(
                self.mouse_state["current_pos"],
                self.current_color,
                0
            )
            self.canvas_view.draw_line(
                self.mouse_state["prev_pos"],
                self.mouse_state["current_pos"],
                self.current_color,
                0
            )
        elif self.current_brush == "stroke":
            self.preview_canvas.copy_content(self.canvas)
            self.canvas_view.draw_line(
                self.mouse_state["start_pos"],
                self.mouse_state["current_pos"],
                self.current_color,
                0
            )
        elif self.current_brush == "picker":
            color = self.canvas_view.get_color(
                self.mouse_state["current_pos"])

            if color is not None:
                self.current_color = color
        elif self.current_brush == "fill":
            self.canvas_view.fill(
                self.mouse_state["current_pos"],
                self.current_color,
                0
            )

    def draw_to_canvas(self):
        self.canvas.copy_content(self.preview_canvas)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    widget.show()

    sys.exit(app.exec())
