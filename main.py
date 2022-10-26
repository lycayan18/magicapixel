import sys

from PIL import Image
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QMenuBar, QAction, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QRect, QPointF, QUrl, Qt
from widgets.canvasview import CanvasView
from widgets.newfilewindow import NewFileWindow
from widgets.colorpicker import ColorPicker
from widgets.resizesettingswindow import ResizeSettingsWindow
from utils.color_converters import convert
from utils.state_manager import StateManager
from utils.keyboard_actions_manager import KeyboardActionsManager
from ui.mainwindow.mainwindow import Ui_MainWindow
from ui.styles.button import CURRENT_BRUSH_BUTTON_STYLESHEET
import magicautils

QApplication.setAttribute(
    Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


class MainWidget(Ui_MainWindow, QWidget):
    def __init__(self):
        super().__init__()

        self.state_manager = StateManager()
        self.keyboard_actions_manager = KeyboardActionsManager()

        self.keyboard_actions_manager.subscribe("Ctrl+Z", self.pop_state)
        self.keyboard_actions_manager.subscribe("Ctrl+Y", self.recover_state)

        # Current editing file
        self.current_file = None

        # Current drawing size
        self.current_width = 96
        self.current_height = 96

        self.canvas = magicautils.Canvas(
            self.current_width, self.current_height)
        self.color_picker = ColorPicker(self.handle_color_change)

        # Canvas for previewing what you're going to draw
        self.preview_canvas = magicautils.Canvas(
            self.current_width, self.current_height)

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
            "canvas_start_pos": QPoint(0, 0),
            "current_pos": QPoint(0, 0),
            "prev_pos": QPoint(0, 0)
        }

        self.initUI()
        self.save_state()

    # As QtDesigner does not supports menu bar in QWidget window, we create it here
    def init_menu_bar(self):
        menu = QMenuBar()
        self.vbox.addWidget(menu)

        file_menu = menu.addMenu("Файл")

        self.new_file_action = QAction("Новый", self)
        self.new_file_action.triggered.connect(self.handle_new_file)

        self.open_file_action = QAction("Открыть", self)
        self.open_file_action.triggered.connect(self.handle_open_file)

        self.save_file_action = QAction("Сохранить", self)
        self.save_file_action.triggered.connect(self.handle_save_file)

        self.save_file_action.setDisabled(True)

        self.save_as_file_action = QAction("Сохранить как...", self)
        self.save_as_file_action.triggered.connect(self.handle_save_as_file)

        self.resize_canvas_action = QAction("Масштабировать", self)
        self.resize_canvas_action.triggered.connect(self.handle_resize_canvas)

        file_menu.addAction(self.new_file_action)
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.save_file_action)
        file_menu.addAction(self.save_as_file_action)
        file_menu.addAction(self.resize_canvas_action)

        menu.setStyleSheet("background: #fff;")

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle("Magica Pixel")
        self.setWindowIcon(QtGui.QIcon("./assets/icon.ico"))

        self.init_menu_bar()

        self.canvas_view.setGeometry(0, 0, 800, 515)
        self.canvas_view.show()

        self.connect_brush_button_handler(self.penButton, "pen")
        self.connect_brush_button_handler(self.strokeButton, "stroke")
        self.connect_brush_button_handler(self.pickerButton, "picker")
        self.connect_brush_button_handler(self.fillButton, "fill")
        self.currentColorButton.clicked.connect(self.open_color_picker)

    def handle_new_file(self):
        new_file_window = NewFileWindow(self.create_new_canvas)
        new_file_window.show()

    def handle_resize_canvas(self):
        resize_settings_window = ResizeSettingsWindow(
            self.resize_canvas_and_save_state)
        resize_settings_window.show()

    def save_state(self):
        self.state_manager.push_state(self.get_state())

    # Return to previous state ( in other words cancel last operation )
    def pop_state(self):
        state = self.state_manager.pop_state()

        if state is not None:
            self.set_state(state)

    # Return to next state ( in other words recover cancelled operation )
    def recover_state(self):
        state = self.state_manager.recover_last_state()

        if state is not None:
            self.set_state(state)

    def get_state(self):
        state = {
            "current_width": self.current_width,
            "current_height": self.current_height,
            "current_file": self.current_file,
            "canvases": [self.canvas.clone()]
        }

        return state

    def set_state(self, state):
        self.current_width = state["current_width"]
        self.current_height = state["current_height"]
        self.current_file = state["current_file"]

        self.save_file_action.setDisabled(self.current_file is None)
        self.update_window_title()

        # Resize view
        self.canvas.resize(self.current_width, self.current_height)
        self.preview_canvas.resize(self.current_width, self.current_height)
        self.canvas_view.resize_view(self.current_width, self.current_height)

        # Copy content
        state["canvases"][0].copy_content(self.canvas)
        self.canvas.copy_content(self.preview_canvas)

        # Redraw
        self.canvas_view.update()
        self.repaint()

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        if ev.isAutoRepeat():
            return super().keyPressEvent(ev)

        self.keyboard_actions_manager.keypress_event(ev.key())

        return super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev: QtGui.QKeyEvent) -> None:
        self.keyboard_actions_manager.keyrelease_event(ev.key())

        return super().keyReleaseEvent(ev)

    # Creates new canvas:
    # Resizes canvas content to fit width and height
    # and clears canvas content
    def create_new_canvas(self, width: int, height: int):
        self.preview_canvas.clear()
        self.canvas.clear()
        self.resize_canvas(width, height)
        self.canvas_view.repaint()
        self.repaint()

        self.current_file = None
        self.save_file_action.setDisabled(True)

        self.update_window_title()

        self.save_state()

    def update_window_title(self):
        if self.current_file is None:
            self.setWindowTitle("Magica Pixel")
            return

        filename = self.current_file.replace("\\", "/", -1).split("/")[-1]

        self.setWindowTitle(f"{filename} - Magica Pixel")

    def resize_canvas_and_save_state(self, width: int, height: int, scale_contents: bool, smooth_scale: bool):
        self.resize_canvas(width, height, scale_contents, smooth_scale)
        self.save_state()

    def resize_canvas(self, width: int, height: int, scale_contents: bool = False, smooth_scale: bool = False):
        self.canvas.resize(width, height, scale_contents, smooth_scale)
        self.preview_canvas.resize(width, height, scale_contents, smooth_scale)
        self.canvas_view.resize_view(width, height)
        self.current_width = width
        self.current_height = height

    def handle_open_file(self):
        filepath: QUrl = QFileDialog.getOpenFileName(
            self, "Save Image", "./", "Images (*.png *.jpg *.jpeg *.bmp *.ico)")[0]

        if filepath != '':
            self.current_file = filepath
            self.save_file_action.setEnabled(True)

            # TODO: Add error handling ( e.g. when file structure is broken )
            im = Image.open(filepath)

            self.resize_canvas(im.width, im.height)
            data = im.load()

            for x in range(im.width):
                for y in range(im.height):
                    self.canvas.set_pixel(x, y, convert(data[x, y], im.mode))

            self.canvas.copy_content(self.preview_canvas)
            self.canvas_view.repaint()
            self.repaint()

            self.save_state()

            self.update_window_title()

    def handle_save_file(self):
        data = magicautils.render_canvases(self.current_width,
                                           self.current_height, [self.canvas])

        im = Image.frombytes(
            "RGBA", (self.current_width, self.current_height), data, "raw")
        im.save(self.current_file)

    def handle_save_as_file(self):
        filepath: QUrl = QFileDialog.getSaveFileName(
            self, "Save Image", "./", "Images (*.png *.jpg *.jpeg *.bmp)")[0]

        if filepath != '':
            self.current_file = filepath
            self.save_file_action.setEnabled(True)

            self.handle_save_file()

            self.update_window_title()

    # Opens color picker window

    def open_color_picker(self):
        self.color_picker.move(self.currentColorButton.x() + self.x() + self.brushPanel.x(),
                               self.currentColorButton.y() + self.y() + self.brushPanel.y())
        self.color_picker.show()

    def handle_color_change(self, color: QtGui.QColor):
        self.current_color = (color.red(), color.green(),
                              color.blue(), color.alpha())

        self.currentColorButton.setStyleSheet(
            f"background: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})")

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

        self.verticalLayoutWidget.resize(ev.size().width(), 23)

        # Use max to bound brushPanel and vbox so nothing overlap each other
        self.brushPanel.move(0, max(ev.size().height() // 2 - 250, 25))

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        # For convenience let's always close the color picker
        # Sometimes you can open color picker and don't close it, forget about it, and with
        # next try opening you may be perplexed: Why it doesn't open?
        self.color_picker.hide()

        self.mouse_state["pressed"] = True
        # Write canvas-relative coordinates instead of window-related. If you won't do that,
        # you'll get a bug: when you start drawing a line and you scale your canvas view or
        # move it your line's starting point also shifts.
        self.mouse_state["canvas_start_pos"] = self.canvas_view.get_canvas_point(
            self.mouse_state["current_pos"])

        self.use_brush()

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_state["pressed"] = False

        self.draw_to_canvas()

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouse_state["prev_pos"] = self.mouse_state["current_pos"]
        self.mouse_state["current_pos"] = ev.pos()

        if self.mouse_state["pressed"]:
            self.canvas_view.highlight_pixel(QPoint(-1, -1))
            self.use_brush()
        else:
            self.canvas_view.highlight_pixel(ev.pos())

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

        self.canvas_view.repaint()
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
            self.canvas.copy_content(self.preview_canvas)
            self.canvas_view.draw_line(
                self.mouse_state["canvas_start_pos"],
                self.canvas_view.get_canvas_point(
                    self.mouse_state["current_pos"]
                ),
                self.current_color,
                0,
                # Do not transform to canvas relative coordinates as they've already been transformed
                transform_to_canvas_relative_coordinates=False
            )
        elif self.current_brush == "picker":
            color = self.canvas_view.get_color(
                self.mouse_state["current_pos"])

            if color is not None:
                qcolor = QtGui.QColor(*color)
                self.handle_color_change(qcolor)
                self.color_picker.set_current_color(qcolor)
        elif self.current_brush == "fill":
            self.canvas_view.fill(
                self.mouse_state["current_pos"],
                self.current_color,
                0
            )

    def draw_to_canvas(self):
        self.canvas_view.highlight_pixel(self.mouse_state["current_pos"])
        self.preview_canvas.copy_content(self.canvas)
        self.save_state()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.color_picker.close()
        return super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    widget.show()

    sys.exit(app.exec())
