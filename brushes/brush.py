from widgets.canvasview import CanvasView

# Brush is a tool for ( any ) interaction with Canvas, whether it be drawing, color picking
# ( and app state changing ), moving canvas, etc.


class Brush:
    def __init__(self, direct_draw: bool):
        """
        :param direct_draw: determines whether brush needs to draw to canvas directly or in preview mode first
        """

        self.direct_draw = direct_draw

    def is_direct_draw_brush(self):
        return self.direct_draw

    def use(self, canvas_view: CanvasView, mouse_state: dict, current_color: tuple[int, int, int, int]):
        """
        Interacts with canvas_view ( f.e. draws )
        :param canvas_view: CanvasView
        :param mouse_state: a dictionary, containing mouse press state, mouse old coordinates,
            current mouse coordinates and start mouse coordinates
        :param current_color: current drawing color
        """
        pass
