from typing import Any
from magicautils import Canvas

# Manages with canvas layers for now, but in future it will manage also with
# canvas frames. In other words, in future I'll add animation support.


class CanvasManager:
    def __init__(self, canvases: list[list[Canvas, str, Any]]):
        # We got link to the array through arguments, so we can easily
        # manipulate this array
        self.canvases = canvases
        self.names = list()
        self.current_editing_canvas = 0

    def set_current_editing_canvas(self, index: int):
        if index < 0 or index >= len(self.canvases):
            return

        self.current_editing_canvas = index

    def get_current_canvas(self) -> Canvas:
        return self.canvases[self.current_editing_canvas][0]

    def get_current_canvas_name(self) -> str:
        return self.canvases[self.current_editing_canvas][1]

    def get_current_canvas_settings(self) -> str:
        return self.canvases[self.current_editing_canvas][2]

    def set_canvas_name(self, index: int, name: str):
        self.canvases[index][1] = name

    def set_canvas_settings(self, index: int, settings):
        self.canvases[index][2] = settings

    def get_current_canvas_index(self) -> int:
        return self.current_editing_canvas

    def add_canvas(self, canvas: Canvas, name: str, settings):
        self.canvases.append([canvas, name, settings])

    def remove_canvas(self, index: int):
        self.canvases.pop(index)

        if self.current_editing_canvas >= len(self.canvases):
            self.current_editing_canvas = len(self.canvases) - 1

    def move_canvas(self, index: int, destination: int):
        if destination < 0 or destination >= len(self.canvases):
            return

        self.canvases.insert(destination, self.canvases.pop(index))

    # Returns tuple with lists of canvases, their names and settings.
    # Needed for render_canvases to pass list of canvases and list of their settings.
    def get_canvases(self):
        canvases = list()
        names = list()
        settings = list()

        for canvas, name, setting in self.canvases:
            canvases.append(canvas)
            names.append(name)
            settings.append(setting)

        return (canvases, names, settings)
