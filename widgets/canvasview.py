import ctypes
from typing import Union
import struct
from PyQt5.QtWidgets import QWidget, QOpenGLWidget
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QImage
from PyQt5.QtCore import QPoint, QObject, QPointF, QSize, QRect
import OpenGL.GL as gl
from shaders.base import VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE
from magicautils import Canvas, render_canvases
import constants.blending as AlphaBlendingModes


class CanvasView(QOpenGLWidget):
    def __init__(self, width: int, height: int, preview_canvas: Canvas, canvases: list[list[Canvas, str, int]], parent: QObject = None):
        super().__init__(parent)
        self.shift = QPointF(0, 0)
        self.scale = 1.0
        self.canvas_width = width
        self.canvas_height = height
        self.display_all_layers = False
        self.preview_canvas = preview_canvas
        self.previewing_canvas = 0
        self.canvases = canvases
        self.highlighted_pixel = QPoint(-1, -1)

    # OpenGL related functions

    def initializeGL(self) -> None:
        program = self.create_shader(
            VERTEX_SHADER_SOURCE, FRAGMENT_SHADER_SOURCE)

        gl.glUseProgram(program)

        vertices = [
            -1.0, -1.0,
            -1.0, +1.0,
            +1.0, -1.0,
            +1.0, -1.0,
            -1.0, +1.0,
            +1.0, +1.0
        ]

        vertex_data = struct.pack("f" * len(vertices), *vertices)

        vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)

        gl.glBufferData(gl.GL_ARRAY_BUFFER, 4 * 2 * 6,
                        vertex_data, gl.GL_DYNAMIC_DRAW)

        position_location = gl.glGetAttribLocation(program, "position")
        gl.glVertexAttribPointer(position_location, 2,
                                 gl.GL_FLOAT, True, 0, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(position_location)

        self.scale_uniform_location = gl.glGetUniformLocation(program, "scale")
        gl.glUniform1f(self.scale_uniform_location, 1.0)

        self.shift_uniform_location = gl.glGetUniformLocation(program, "shift")
        gl.glUniform2f(self.shift_uniform_location, 0, 0)

        self.screen_size_location = gl.glGetUniformLocation(
            program, "screenSize")

        self.canvas_size_location = gl.glGetUniformLocation(
            program, "canvasSize")

        gl.glUniform2f(self.screen_size_location, self.width(), self.height())
        gl.glUniform2f(self.canvas_size_location,
                       self.canvas_width, self.canvas_height)

        self.sampler_location = gl.glGetUniformLocation(
            program, "textureSampler")

        gl.glUniform1i(self.sampler_location, 0)

        texture_data = self.render_canvases()

        self.view_texture = self.create_texture2D(
            self.canvas_width, self.canvas_height, texture_data)

    def create_shader(self, vertex_source: str, fragment_source: str):
        vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

        gl.glShaderSource(vertex, vertex_source)
        gl.glShaderSource(fragment, fragment_source)

        gl.glCompileShader(vertex)

        if not gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS):
            log = gl.glGetShaderInfoLog(vertex).decode()

            raise RuntimeError("Cannot compile vertex shader:\n", log)

        gl.glCompileShader(fragment)

        if not gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS):
            log = gl.glGetShaderInfoLog(fragment).decode()

            raise RuntimeError("Cannot compile fragment shader:\n", log)

        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex)
        gl.glAttachShader(program, fragment)
        gl.glLinkProgram(program)

        if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
            log = gl.glGetProgramInfoLog(program)

            raise RuntimeError("Cannot link program:\n", log)

        gl.glDetachShader(program, vertex)
        gl.glDetachShader(program, fragment)

        return program

    def create_texture2D(self, width: int, height: int, data: bytes):
        buffer = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, buffer)

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width,
                        height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)

        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        return buffer

    def set_texture_data(self, texture, width: int, height: int, data: bytes):
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width,
                        height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)

        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def paintGL(self) -> None:
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUniform2f(self.canvas_size_location,
                       self.canvas_width, self.canvas_height)
        gl.glUniform1f(self.scale_uniform_location, self.scale)
        gl.glUniform2f(self.shift_uniform_location,
                       self.shift.x(), self.shift.y())
        gl.glUniform2f(self.screen_size_location, self.width(), self.height())

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.view_texture)
        gl.glUniform1i(self.sampler_location, 0)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

    def render_canvases(self) -> bytes:
        # Create new canvases array to change current editing layer canvas
        # to preview canvas to see changes in current editing layer and don't
        # mess up original canvases array

        canvases = list()
        alpha_blendings = list()

        if self.display_all_layers:
            for canvas, name, alpha_blending in self.canvases:
                canvases.append(canvas)
                alpha_blendings.append(alpha_blending)

            canvases[self.previewing_canvas] = self.preview_canvas
        else:
            canvases.append(self.preview_canvas)
            # Keep blending mode for WYSIWYG
            alpha_blendings.append(self.canvases[self.previewing_canvas][2])

        texture_data: bytes = render_canvases(
            self.canvas_width, self.canvas_height,
            canvases, alpha_blendings,
            self.highlighted_pixel.x(), self.highlighted_pixel.y())

        return texture_data

    def update_view_texture(self):
        texture_data = self.render_canvases()

        self.set_texture_data(
            self.view_texture, self.canvas_width, self.canvas_height, texture_data)

        del texture_data

    # Canvas view related functions

    def set_display_all_layers(self, enabled: bool):
        self.display_all_layers = enabled
        self.update_view()

    def set_current_previewing_layer(self, index: int):
        if index < 0 or index >= len(self.canvases):
            return

        self.previewing_canvas = index

    def shift_by(self, shift: QPoint):
        self.shift += shift

    def set_shift(self, shift: QPoint):
        self.shift = shift

    def scale_by(self, scale: float):
        self.scale *= scale

    def set_scale(self, scale: float):
        self.scale = scale

    def resize_view(self, width: int, height: int):
        self.canvas_width = width
        self.canvas_height = height

    def update_view(self):
        self.update_view_texture()
        self.repaint()

    def get_canvas_point(self, mouse: QPoint) -> QPoint:
        # To avoid inaccuracy we do all calculations in float
        out: QPointF = (QPointF(mouse) - QPointF(self.shift) -
                        QPointF(self.width(), self.height()) * 0.5) / self.scale

        return QPoint(int(out.x()), int(out.y()))

    def get_color(self, at: QPoint, canvas: int = 0) -> Union[tuple[int, int, int, int], None]:
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return None

        return self.preview_canvas.get_pixel(point.x(), point.y())

    def draw_pixel(self, at: QPoint, color: tuple[int, int, int, int], canvas: int = 0):
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return

        self.preview_canvas.set_pixel(point.x(), point.y(), tuple(color))
        self.update_view_texture()
        self.repaint()

    def draw_line(self, p0: QPoint, p1: QPoint, color: tuple[int, int, int, int], canvas: int = 0, transform_to_canvas_relative_coordinates=True):
        start = p0
        end = p1

        if transform_to_canvas_relative_coordinates:
            start = self.get_canvas_point(p0)
            end = self.get_canvas_point(p1)

        self.preview_canvas.draw_line(
            start.x(), start.y(), end.x(), end.y(), tuple(color))

        self.update_view_texture()
        self.repaint()

    def fill(self, at: QPoint, color: tuple[int, int, int, int], canvas: int = 0):
        point = self.get_canvas_point(at)

        if point.x() < 0 or point.x() >= self.canvas_width or point.y() < 0 or point.y() >= self.canvas_height:
            return

        self.preview_canvas.fill(point.x(), point.y(), tuple(color))

        self.update_view_texture()
        self.repaint()

    def highlight_pixel(self, at: QPoint):
        self.highlighted_pixel = self.get_canvas_point(at)
        self.update_view_texture()
        self.repaint()
