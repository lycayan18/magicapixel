from PIL import Image, ImageDraw
from canvas import Canvas


def render_canvases(width: int, height: int, canvases: list[Canvas]) -> Image:
    im = Image.new("RGBA", (width, height), "#0000")
    drawer = ImageDraw.Draw(im)

    for y in range(height):
        for x in range(width):
            color = [0, 0, 0, 0]

            for canvas in canvases:
                # Convert channels to float 0-1 range
                pixel = [i / 255 for i in canvas.get_pixel(x, y)]

                # Apply alpha blending
                a_coef = pixel[3] * (1 - color[3])

                color[0] = color[0] * color[3] + pixel[0] * a_coef
                color[1] = color[1] * color[3] + pixel[1] * a_coef
                color[2] = color[2] * color[3] + pixel[2] * a_coef
                color[3] = color[3] + a_coef

            color[0] = int(color[0] * 255)
            color[1] = int(color[1] * 255)
            color[2] = int(color[2] * 255)
            color[3] = int(color[3] * 255)

            drawer.point((x, y), tuple(color))

    return im