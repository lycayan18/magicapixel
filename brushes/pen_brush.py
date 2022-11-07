from brushes.brush import Brush


class PenBrush(Brush):
    def __init__(self):
        super().__init__(True)

    def use(self, canvas_view, mouse_state, current_color):
        # Keep it here in case we want to add extra functionality to base class
        super().use(canvas_view, mouse_state, current_color)

        # To prevent "bubbles" we need to draw the line from mouse previous
        # position to mouse current position
        # Otherwise, you'll see "holes"
        canvas_view.draw_pixel(
            mouse_state["current_pos"],
            current_color,
            0
        )

        canvas_view.draw_line(
            mouse_state["prev_pos"],
            mouse_state["current_pos"],
            current_color,
            0
        )
