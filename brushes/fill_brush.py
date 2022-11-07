from PyQt5.QtGui import QColor
from brushes.brush import Brush


class FillBrush(Brush):
    def __init__(self):
        super().__init__(True)

    def use(self, canvas_view, mouse_state, current_color):
        # Keep it here in case we want to add extra functionality to base class
        super().use(canvas_view, mouse_state, current_color)

        canvas_view.fill(
            mouse_state["current_pos"],
            current_color,
            0
        )
