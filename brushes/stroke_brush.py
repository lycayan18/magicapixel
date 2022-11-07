from brushes.brush import Brush


class StrokeBrush(Brush):
    def __init__(self):
        super().__init__(False)

    def use(self, canvas_view, mouse_state, current_color):
        # Keep it here in case we want to add extra functionality to base class
        super().use(canvas_view, mouse_state, current_color)

        canvas_view.draw_line(
            mouse_state["canvas_start_pos"],
            canvas_view.get_canvas_point(
                mouse_state["current_pos"]
            ),
            current_color,
            0,
            # Do not transform to canvas relative coordinates as they've already been transformed
            transform_to_canvas_relative_coordinates=False
        )
