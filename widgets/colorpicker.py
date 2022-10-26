from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QImage, QMouseEvent, QIcon, QCursor
from PyQt5.QtCore import QObject, Qt, QPoint, QRectF, QRect
from ui.styles.lineedit import LIGHT_LINEEDIT_STYLESHEET
from ui.styles.button import LIGHT_BUTTON_STYLESHEET


class ColorPicker(QWidget):
    def __init__(self, color_changed, parent: QObject = None):
        super().__init__(parent)

        self.color_changed_callback = color_changed

        self.current_hue = 0
        self.current_value = 255
        self.current_saturation = 0
        self.current_alpha = 255

        # Flags
        self.changing_saturation_value = False
        self.changing_hue = False

        # Saturation/volume rect
        self.sv_rect = QImage(255, 255, QImage.Format.Format_RGB888)
        self.hue_line = QImage(30, 255, QImage.Format.Format_RGB888)

        self.prepare_images()
        self.initUI()

    def initUI(self):
        self.setFixedSize(310, 300)
        self.setWindowTitle("Choose color")
        self.setWindowIcon(QIcon("./assets/icon.ico"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.okButton = QPushButton("OK", self)
        self.okButton.clicked.connect(self.hide)
        self.okButton.move(215, 265)
        self.okButton.resize(40, 25)
        self.okButton.setStyleSheet(LIGHT_BUTTON_STYLESHEET)
        self.okButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.rgbInput = QLineEdit(self)
        self.rgbInput.resize(200, 25)
        self.rgbInput.move(10, 265)

        self.rgbInput.setText("rgba(255, 255, 255, 255)")
        self.rgbInput.textEdited.connect(self.handle_rgb_input)
        self.rgbInput.setStyleSheet(LIGHT_LINEEDIT_STYLESHEET)

    def set_current_color(self, color: QColor):
        if color.hue() != -1:
            self.current_hue = color.hue()

        self.current_saturation = color.saturation()
        self.current_value = color.value()

        self.rgbInput.setText(
            f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})")

        self.update_saturation_volume_rect()

    def handle_rgb_input(self):
        rgbstring = self.rgbInput.text()

        if (not rgbstring.startswith("rgba(") or
                not rgbstring.endswith(')')):
            return

        channels = rgbstring[5:-1].split(',')

        color = QColor(0, 0, 0)

        if len(channels) > 0:
            if channels[0].strip().isdecimal():
                # Clamp channel value up to 255
                color.setRed(min(int(channels[0]), 255))
            else:
                return
        else:
            return

        if len(channels) > 1:
            if channels[1].strip().isdecimal():
                # Clamp channel value up to 255
                color.setGreen(min(int(channels[1]), 255))
            else:
                return

        if len(channels) > 2:
            if channels[2].strip().isdecimal():
                # Clamp channel value up to 255
                color.setBlue(min(int(channels[2]), 255))
            else:
                return

        if len(channels) > 3:
            if channels[2].strip().isdecimal():
                # Clamp channel value up to 255
                color.setAlpha(min(int(channels[3]), 255))
            else:
                return

        hsv = color.toHsv()

        self.current_hue = hsv.hue()

        if self.current_hue == -1:
            self.current_hue = 0

        self.current_saturation = hsv.saturation()
        self.current_value = hsv.value()
        self.current_alpha = color.alpha()

        self.color_changed_callback(
            QColor.fromHsv(
                int(self.current_hue),
                int(self.current_saturation),
                int(self.current_value),
                int(self.current_alpha)
            )
        )

        self.update_saturation_volume_rect()
        self.repaint()

    # Pre-draw rarely-updated parts of ui and save them as images
    def prepare_images(self):
        for v in range(255):
            for s in range(255):
                self.sv_rect.setPixelColor(
                    s, 254 - v,
                    QColor.fromHsv(self.current_hue, s, v)
                )

        for h in range(255):
            for x in range(30):
                self.hue_line.setPixelColor(
                    x, h,
                    QColor.fromHsv(int(h / 255 * 359), 255, 255)
                )

    def update_saturation_volume_rect(self):
        for v in range(255):
            for s in range(255):
                self.sv_rect.setPixelColor(
                    s, 254 - v,
                    QColor.fromHsv(self.current_hue, s, v)
                )

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        mouse_x = ev.x()
        mouse_y = ev.y()

        if mouse_x <= 255 and mouse_y <= 255:
            self.changing_saturation_value = True
        elif mouse_x >= 270 and mouse_x <= 300 and mouse_y <= 255:
            self.changing_hue = True

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.changing_saturation_value = False
        self.changing_hue = False

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        mouse_x = ev.x()
        mouse_y = ev.y()

        if self.changing_saturation_value:
            # Edit saturation/volume
            # To avoid out of range values we clamp coordinates between 0 and 255
            self.choose_saturation_volume(
                min(max(mouse_x, 0), 255),
                min(max(mouse_y, 0), 255)
            )

            self.color_changed_callback(
                QColor.fromHsv(
                    self.current_hue,
                    self.current_saturation,
                    self.current_value,
                    self.current_alpha
                )
            )
        elif self.changing_hue:
            # To avoid out of range values we clamp y between 0 and 255
            self.choose_hue(min(max(mouse_y, 0), 255))

            self.color_changed_callback(
                QColor.fromHsv(
                    self.current_hue,
                    self.current_saturation,
                    self.current_value,
                    self.current_alpha
                )
            )

        self.repaint()

    def choose_saturation_volume(self, mx: int, my: int):
        self.current_saturation = mx
        self.current_value = 255 - my

        rgb = QColor.fromHsv(
            self.current_hue,
            self.current_saturation,
            self.current_value,
            self.current_alpha
        )

        self.rgbInput.setText(
            f"rgba({rgb.red()}, {rgb.green()}, {rgb.blue()}, {rgb.alpha()})")

    def choose_hue(self, my: int):
        self.current_hue = int(my / 255 * 359)
        self.update_saturation_volume_rect()

    def paintEvent(self, ev: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(QRect(0, 0, 310, 300), QColor(50, 50, 50))

        painter.drawImage(QPoint(0, 0), self.sv_rect)
        painter.drawImage(QPoint(270, 0), self.hue_line)

        painter.setPen(QColor(255, 255, 255))
        painter.drawArc(
            QRectF(
                self.current_saturation - 4, 255 - self.current_value - 4,
                8, 8
            ),
            0, 360 * 16
        )

        painter.drawRect(QRectF(265, self.current_hue / 360 * 255 - 3, 40, 6))
        painter.drawRect(QRectF(266, self.current_hue / 360 * 255 - 2, 38, 4))

        painter.fillRect(
            QRect(270, 260, 30, 30),
            QColor.fromHsv(
                self.current_hue,
                self.current_saturation,
                self.current_value,
                self.current_alpha
            )
        )
