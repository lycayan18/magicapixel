from typing import Union
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QImage
from PyQt5.QtCore import QPoint, QObject, QPointF, QSize, QRect
from canvas import Canvas
import time


class CanvasView(QWidget):
    def __init__(self, width: int, height: int, *canvases: Canvas, parent: QObject = None):
        super().__init__(parent)
        self.shift = QPointF(0, 0)
        self.scale = 1.0
        self.canvas_width = width
        self.canvas_height = height
        self.canvases = list(canvases)
        self.highlighted_pixel = QPoint(-1, -1)

    def shift_by(self, shift: QPoint):
        self.shift += shift

    def set_shift(self, shift: QPoint):
        self.shift = shift

    def scale_by(self, scale: float):
        self.scale *= scale

    def set_scale(self, scale: float):
        self.scale = scale

    def resize_view(self, width: int, height: int):
        self.canvas_width = width
        self.canvas_height = height

    def paintEvent(self, ev: QPaintEvent):
        painter: QPainter = QPainter(self)
        canvas_window_width = int(self.canvas_width * self.scale)
        canvas_window_height = int(self.canvas_height * self.scale)

        start = time.time()

        # [0 for _ in range(self.canvas_width * self.canvas_height * 4)]
        data = []

        operations = 0

        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                operations += 1
                color = [0, 0, 0, 0]

                for canvas in self.canvases:
                    # Convert channels to float 0-1 range
                    # [i / 255 for i in canvas.get_pixel(x, y)]
                    pixel = [i / 255 for i in canvas.get_pixel(x, y)]

                    # Apply alpha blending
                    a_coef = pixel[3] * (1 - color[3])

                    color[0] = color[0] * color[3] + pixel[0] * a_coef
                    color[1] = color[1] * color[3] + pixel[1] * a_coef
                    color[2] = color[2] * color[3] + pixel[2] * a_coef
                    color[3] = color[3] + a_coef

                color[0] = int(color[0] * 255)
                color[1] = int(color[1] * 255)
                color[2] = int(color[2] * 255)
                color[3] = int(color[3] * 255)

                if x == self.highlighted_pixel.x() and y == self.highlighted_pixel.y():
                    if color[0] + color[1] + color[2] < 110 * 3:
                        color[0] = min(color[0] + 60, 255)
                        color[1] = min(color[1] + 60, 255)
                        color[2] = min(color[2] + 60, 255)
                    else:
                        color[0] = max(color[0] - 60, 0)
                        color[1] = max(color[1] - 60, 0)
                        color[2] = max(color[2] - 60, 0)

                data.append(color[0])
                data.append(color[1])
                data.append(color[2])
                data.append(color[3])

        # print(1 / (time.time() - start))

        rendered_view = QImage(
            bytes(data),
            self.canvas_width, self.canvas_height,
            QImage.Format.Format_RGBA8888
        )

        scaled_view = rendered_view.scaled(
            canvas_window_width, canvas_window_height)

        painter.drawImage(QPoint(self.width(), self.height())
                          * 0.5 + self.shift, scaled_view)

    def get_canvas_point(self, mouse: QPoint) -> QPoint:
        # To avoid inaccuracy we do all calculations in float
        out: QPointF = (QPointF(mouse) - QPointF(self.shift) -
                        QPointF(self.width(), self.height()) * 0.5) / self.scale

        return QPoint(int(out.x()), int(out.y()))

    def get_color(self, at: QPoint, canvas: int = 0) -> Union[tuple[int, int, int, int], None]:
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return None

        return self.canvases[canvas].get_pixel(point.x(), point.y())

    def draw_pixel(self, at: QPoint, color: tuple[int, int, int, int], canvas: int = 0):
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return

        self.canvases[canvas].set_pixel(point.x(), point.y(), color)
        self.repaint()

    def draw_line(self, p0: QPoint, p1: QPoint, color: tuple[int, int, int, int], canvas: int = 0, transform_to_canvas_relative_coordinates=True):
        start = p0
        end = p1

        if transform_to_canvas_relative_coordinates:
            start = self.get_canvas_point(p0)
            end = self.get_canvas_point(p1)

        self.canvases[canvas].draw_line(
            start.x(), start.y(), end.x(), end.y(), color)

        self.repaint()

    def fill(self, at: QPoint, color: tuple[int, int, int, int], canvas: int = 0):
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return

        self.canvases[canvas].fill(point.x(), point.y(), tuple(color))

        self.repaint()

    def highlight_pixel(self, at: QPoint):
        self.highlighted_pixel = self.get_canvas_point(at)
        self.repaint()
