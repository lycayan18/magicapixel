from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from ui.styles.button import BRUSH_BUTTON_STYLESHEET, CURRENT_BRUSH_BUTTON_STYLESHEET

# A typical button with extra functions, such as highlighting


class BrushButton(QPushButton):
    def __init__(self, icon: QIcon, parent=None):
        super().__init__(icon, "", parent)

        self.setIcon(icon)
        self.setIconSize(QSize(24, 24))
        self.setFlat(False)

    def set_highlighted(self, highlighted: bool):
        """
        Sets highlighted stylesheet or recovers back to default
        """

        styles = {
            0: BRUSH_BUTTON_STYLESHEET,  # false
            1: CURRENT_BRUSH_BUTTON_STYLESHEET  # true
        }

        self.setStyleSheet(styles[int(highlighted)])
