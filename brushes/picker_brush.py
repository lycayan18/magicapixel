from typing import Callable
from PyQt5.QtGui import QColor
from brushes.brush import Brush


class PickerBrush(Brush):
    def __init__(self, on_color_picked_callback: Callable[[QColor], None]):
        """
        :param on_color_picked_callback: calls when color has been picked
        """

        super().__init__(True)

        self.on_color_picked_callback = on_color_picked_callback

    def use(self, canvas_view, mouse_state, current_color):
        # Keep it here in case we want to add extra functionality to base class
        super().use(canvas_view, mouse_state, current_color)

        color = canvas_view.get_color(mouse_state["current_pos"])

        if color is not None:
            self.on_color_picked_callback(QColor(*color))
