class Canvas:
    def __init__(self, width: int, height: int):
        self.canvas = list()

        for i in range(width * height):
            self.canvas.append((0, 0, 0, 255))

        self.width = width
        self.height = height

    def set_pixel(self, x: int, y: int, rgba: tuple[int, int, int, int]):
        self.canvas[x + y * self.width] = tuple(rgba)

    def get_pixel(self, x: int, y: int):
        return self.canvas[x + y * self.width]
