class Canvas:
    def __init__(self, width: int, height: int):
        self.canvas = list()

        for i in range(width * height):
            self.canvas.append((0, 0, 0, 255))

        self.width = width
        self.height = height

    def set_pixel(self, x: int, y: int, rgba: tuple[int, int, int, int]):
        self.canvas[x + y * self.width] = tuple(rgba)

    def get_pixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        return self.canvas[x + y * self.width]

    # Canvas sizes must be identical!
    def copy_content(self, canvas):
        for i in range(self.width * self.height):
            self.canvas[i] = canvas.canvas[i]

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]):
        # Bresenham's algorithm
        # If you remove these 2 rows you can get minor bug: sometimes first and last point may not be rendered
        if x0 >= 0 and x0 < self.width and y0 >= 0 and y0 < self.height:
            self.set_pixel(x0, y0, color)

        if x1 >= 0 and x1 < self.width and y1 >= 0 and y1 < self.height:
            self.set_pixel(x1, y1, color)

        for x in range(min(x0, x1), max(x0, x1)):
            y = round((y1 - y0) / (x1 - x0) * (x - x0) + y0)

            if round(x) < 0 or round(x) >= self.width or y < 0 or y >= self.height:
                continue

            # Round coordinates to avoid line thickening in some places
            self.set_pixel(round(x), round(y), color)

        for y in range(min(y0, y1), max(y0, y1)):
            x = round((x1 - x0) / (y1 - y0) * (y - y0) + x0)

            if x < 0 or x >= self.width or round(y) < 0 or round(y) >= self.height:
                continue

            # Round coordinates to avoid line thickening in some places
            self.set_pixel(round(x), round(y), color)

    def fill(self, x: int, y: int, color: tuple[int, int, int, int]):
        start_color = self.get_pixel(x, y)

        if start_color == color:
            return

        pixels = list()
        pixels.append((x, y))

        while len(pixels) > 0:
            pixel = pixels.pop(0)

            self.set_pixel(*pixel, color)

            if pixel[0] - 1 >= 0:
                left = (pixel[0] - 1, pixel[1])

                if self.get_pixel(*left) == start_color and left not in pixels:
                    pixels.append(left)

            if pixel[0] + 1 < self.width:
                right = (pixel[0] + 1, pixel[1])

                if self.get_pixel(*right) == start_color and right not in pixels:
                    pixels.append(right)

            if pixel[1] - 1 >= 0:
                bottom = (pixel[0], pixel[1] - 1)

                if self.get_pixel(*bottom) == start_color and bottom not in pixels:
                    pixels.append(bottom)

            if pixel[1] + 1 < self.height:
                top = (pixel[0], pixel[1] + 1)

                if self.get_pixel(*top) == start_color and top not in pixels:
                    pixels.append(top)

    def clear(self, color: tuple[int, int, int, int] = (0, 0, 0, 255)):
        for i in range(self.width * self.height):
            self.canvas[i] = color
