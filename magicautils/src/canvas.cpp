#include <math.h>
#include <vector>
#include <stdlib.h>
#include "canvas.h"
#include "vec2.h"
#include "clamp.h"
#include "pixelutils.h"
#include "color.h"

extern "C"
{

PyObject *canvas_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    canvasobject *self;
    self = (canvasobject*)type->tp_alloc(type, 0);

    if (self != NULL)
    {
        self->data = NULL;
        self->width = 0;
        self->height = 0;
    }

    return (PyObject *)self;
}

void canvas_dealloc(canvasobject *self)
{
    delete[] self->data;

    Py_TYPE(self)->tp_free((PyObject *)self);
}

int canvas_init(canvasobject *self, PyObject *args, PyObject *kwds)
{
    PyObject *width = NULL;
    PyObject *height = NULL;

    if(!PyArg_ParseTuple(args, "|OO", &width, &height))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas(width: int, height: int): Expected two ints in constructor.");
        return -1;
    }

    // Get variables by keywords if they weren't provided by args

    if(width == NULL && PyMapping_HasKeyString(kwds, "width"))
    {
        width = PyMapping_GetItemString(kwds, "width");
    }

    if(height == NULL && PyMapping_HasKeyString(kwds, "height"))
    {
        height = PyMapping_GetItemString(kwds, "height");
    }

    if(width != NULL)
    {
        if(PyLong_Check(width))
        {
            self->width = PyLong_AsLong(width);
        }
        else
        {
            PyTypeObject *type = (PyTypeObject*)PyObject_Type(width);
            char errorMessageBuffer[1024];

            sprintf(errorMessageBuffer, "Canvas(width: int, height: int): Expected type \"int\", but got \"%s\".", type->tp_name);

            PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            return -1;
        }
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "Canvas(width: int, height: int): \"width\" argument is not provided.");
        return -1;
    }

    if(height != NULL)
    {
        if(PyLong_Check(height))
        {
            self->height = PyLong_AsLong(height);
        }
        else
        {
            PyTypeObject *type = (PyTypeObject*)PyObject_Type(height);
            char errorMessageBuffer[1024];

            sprintf(errorMessageBuffer, "Canvas(width: int, height: int): Expected type \"int\", but got \"%s\".", type->tp_name);

            PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            return -1;
        }
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, "Canvas(width: int, height: int): \"width\" argument is not provided.");
        return -1;
    }

    self->data = new unsigned char [self->width * self->height * 4];

    for(unsigned int i = 0; i < self->width * self->height * 4; i++)
    {
        self->data[i] = 0;
    }

    return 0;
}

PyObject *canvas_setPixel(canvasobject *self, PyObject *args)
{
    int x, y;
    int r = 0, g = 0, b = 0, a = 0;
    PyObject* color;

    if(!PyArg_ParseTuple(args, "iiO", &x, &y, &color))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected two ints and one tuple.");
        return NULL;
    }

    if(PyTuple_Check(color))
    {
        if(PyTuple_GET_SIZE(color) == 4)
        {
            PyObject *rObject = PyTuple_GetItem(color, 0);
            PyObject *gObject = PyTuple_GetItem(color, 1);
            PyObject *bObject = PyTuple_GetItem(color, 2);
            PyObject *aObject = PyTuple_GetItem(color, 3);

            if(PyLong_Check(rObject))
            {
                r = PyLong_AsLong(rObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(rObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(gObject))
            {
                g = PyLong_AsLong(gObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(gObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(bObject))
            {
                b = PyLong_AsLong(bObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(bObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(aObject))
            {
                a = PyLong_AsLong(aObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(aObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }
        }
        else
        {
            char errorMessageBuffer[1024];

            sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Provided \"color\" has length %i, but expected 4.", PySequence_Fast_GET_SIZE(color));

            PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            return NULL;
        }
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(color);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Expected \"tuple\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    r = clamp(r, 0, 255);
    g = clamp(g, 0, 255);
    b = clamp(b, 0, 255);
    a = clamp(a, 0, 255);

    // Check that pixel bounds in canvas
    if(x < 0 || x >= self->width || y < 0 || y >= self->height)
    {
        Py_INCREF(Py_None);
        return Py_None;
    }

    setPixel(self->data, x, y, self->width, r, g, b, a);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *canvas_getPixel(canvasobject *self, PyObject *args)
{
    int x, y;

    if(!PyArg_ParseTuple(args, "ii", &x, &y))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.get_pixel(x: int, y: int): Expected two ints.");
        return NULL;
    }

    // Check that pixel bounds in canvas
    if(x < 0 || x >= self->width || y < 0 || y >= self->height)
    {
        Py_INCREF(Py_None);
        return Py_None;
    }

    unsigned int r, g, b, a;

    getPixel(self->data, x, y, self->width, &r, &g, &b, &a);

    PyObject *color = PyTuple_New(4);

    PyTuple_SetItem(color, 0, PyLong_FromLong(r));
    PyTuple_SetItem(color, 1, PyLong_FromLong(g));
    PyTuple_SetItem(color, 2, PyLong_FromLong(b));
    PyTuple_SetItem(color, 3, PyLong_FromLong(a));

    return color;
}

PyObject *canvas_resize(canvasobject *self, PyObject *args)
{
    int width, height;
    bool resizeCanvasContents = false;
    bool smoothResize = false;

    if(!PyArg_ParseTuple(args, "ii|bb", &width, &height, &resizeCanvasContents, &smoothResize))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.resize(width: int, height: int, resize_canvas_contents: bool = False, smooth_resize: bool = False): Expected two ints and one boolean.");
        return NULL;
    }

    unsigned char* oldData = self->data;

    // TODO: Add canvas scaling

    self->data = new unsigned char[width * height * 4];

    for(unsigned int i = 0; i < width * height * 4; i++)
    {
        self->data[i] = 0;
    }

    if(resizeCanvasContents)
    {
        float xScaleFactor = float(self->width) / float(width);
        float yScaleFactor = float(self->height) / float(height);

        // Scale image
        for(unsigned int x = 0; x < width; x++)
        {
            for(unsigned int y = 0; y < height; y++)
            {
                // Relative to old canvas coordinates
                if(smoothResize)
                {
                    float scaledX = float(x) * xScaleFactor;
                    float scaledY = float(y) * yScaleFactor;

                    unsigned int r = 0, g = 0, b = 0, a = 0;

                    // If we scale image down, get average color of pixels
                    if(xScaleFactor > 1)
                    {
                        for(float sx = scaledX; sx < scaledX + xScaleFactor; sx++)
                        {
                            color4_t row = {0, 0, 0, 0};

                            if(yScaleFactor > 1)
                            {
                                for(float sy = scaledY; sy < scaledY + yScaleFactor; sy++)
                                {
                                    color4_t column;

                                    // We can use here usual "getPixel", which would be faster, than getPixelSmoothColor, but for
                                    // qualitative image scaling we use "getPixelSmoothColor"
                                    getPixelSmoothColor(oldData, sx, sy, self->width, self->height, &column.r, &column.g, &column.b, &column.a);

                                    row.r += column.r;
                                    row.g += column.g;
                                    row.b += column.b;
                                    row.a += column.a;
                                }

                                row.r /= ceilf(yScaleFactor);
                                row.g /= ceilf(yScaleFactor);
                                row.b /= ceilf(yScaleFactor);
                                row.a /= ceilf(yScaleFactor);
                            }
                            else
                            {
                                // We can use here usual "getPixel", which would be faster, than getPixelSmoothColor, but for
                                // qualitative image scaling we use "getPixelSmoothColor"
                                getPixelSmoothColor(oldData, sx, scaledY, self->width, self->height, &row.r, &row.g, &row.b, &row.a);
                            }

                            r += row.r;
                            g += row.g;
                            b += row.b;
                            a += row.a;
                        }

                        r /= ceilf(xScaleFactor);
                        g /= ceilf(xScaleFactor);
                        b /= ceilf(xScaleFactor);
                        a /= ceilf(xScaleFactor);
                    }
                    else
                    {
                        // We scale image up, get linearly interpolated color
                        getPixelSmoothColor(oldData, scaledX, scaledY, self->width, self->height, &r, &g, &b, &a);
                    }

                    setPixel(self->data, x, y, width, r, g, b, a);
                }
                else
                {
                    unsigned int scaledX = (unsigned int)(float(x) * xScaleFactor);
                    unsigned int scaledY = (unsigned int)(float(y) * yScaleFactor);

                    unsigned int r, g, b, a;

                    getPixel(oldData, (unsigned int)scaledX, (unsigned int)scaledY, self->width, &r, &g, &b, &a);

                    setPixel(self->data, x, y, width, r, g, b, a);
                }
            }
        }
    }
    else
    {
        // Keep original image in left-top corner

        // Clamp content width to avoid writing in out of bounds
        unsigned int contentWidth = min(self->width, width);
        unsigned int contentHeight = min(self->height, height);

        for(unsigned int x = 0; x < contentWidth; x++)
        {
            for(unsigned int y = 0; y < contentHeight; y++)
            {
                unsigned int r, g, b, a;
                getPixel(oldData, x, y, self->width, &r, &g, &b, &a);
                setPixel(self->data, x, y, width, r, g, b, a);
            }
        }
    }

    self->width = width;
    self->height = height;

    delete[] oldData;

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *canvas_copyContent(canvasobject *self, PyObject *args)
{
    PyObject* target;

    if(!PyArg_ParseTuple(args, "O", &target))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.copy_content(target: Canvas): Expected canvas.");
        return NULL;
    }

    if(PyCanvas_Check(target))
    {
        canvasobject* targetCanvas = (canvasobject*)target;

        // Check that width and height are identical to avoid segmentation fault
        if(targetCanvas->width == self->width && targetCanvas->height == self->height)
        {
            // FIXME: Think about effective copying method
            unsigned int *target = (unsigned int*)targetCanvas->data;
            unsigned int *data = (unsigned int*)self->data;
            for(unsigned int i = 0; i < self->width * self->height; i++)
            {
                target[i] = data[i];
            }
            // memcpy(targetCanvas->data, self->data, self->width * self->height * 4);
        }
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(target);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "Canvas.copy_content(target: Canvas): Expected \"Canvas\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *canvas_drawLine(canvasobject *self, PyObject *args)
{
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    PyObject *color;

    if(!PyArg_ParseTuple(args, "iiiiO", &x0, &y0, &x1, &y1, &color))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected four ints and one tuple.");
        return NULL;
    }

    unsigned int r = 0, g = 0, b = 0, a = 0;

    if(PyTuple_Check(color))
    {
        if(PyTuple_GET_SIZE(color) == 4)
        {
            PyObject *rObject = PyTuple_GetItem(color, 0);
            PyObject *gObject = PyTuple_GetItem(color, 1);
            PyObject *bObject = PyTuple_GetItem(color, 2);
            PyObject *aObject = PyTuple_GetItem(color, 3);

            if(PyLong_Check(rObject))
            {
                r = PyLong_AsLong(rObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(rObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(gObject))
            {
                g = PyLong_AsLong(gObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(gObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(bObject))
            {
                b = PyLong_AsLong(bObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(bObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(aObject))
            {
                a = PyLong_AsLong(aObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(aObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }
        }
        else
        {
            char errorMessageBuffer[1024];

            sprintf(errorMessageBuffer, "draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Provided \"color\" has length %i, but expected 4.", PySequence_Fast_GET_SIZE(color));

            PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            return NULL;
        }
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(color);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Expected \"tuple\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
    }

    r = clamp(r, 0, 255);
    g = clamp(g, 0, 255);
    b = clamp(b, 0, 255);
    a = clamp(a, 0, 255);

    // If you remove these rows you can get minor bug: sometimes first and last point may not be rendered
    if(x0 >= 0 && x0 < self->width && y0 >= 0 && y0 < self->height)
    {
        setPixel(self->data, x0, y0, self->width, r, g, b, a);
    }

    if(x1 >= 0 && x1 < self->width && y1 >= 0 && y1 < self->height)
    {
        setPixel(self->data, x1, y1, self->width, r, g, b, a);
    }

    // Use Bresenham's algorithm

    int xStart = min(x0, x1);
    int xEnd = max(x0, x1);

    for(int x = xStart; x < xEnd; x++)
    {
        int y = roundf(float(y1 - y0) * float(x - x0) / float(x1 - x0) + float(y0));

        if(x < 0 || x >= self->width || y < 0 || y > self->height)
        {
            continue;
        }

        setPixel(self->data, x, y, self->width, r, g, b, a);
    }

    int yStart = min(y0, y1);
    int yEnd = max(y0, y1);

    for(int y = yStart; y < yEnd; y++)
    {
        int x = roundf(float(x1 - x0) * float(y - y0) / float(y1 - y0) + float(x0));

        if(x < 0 || x >= self->width || y < 0 || y > self->height)
        {
            continue;
        }

        setPixel(self->data, x, y, self->width, r, g, b, a);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *canvas_fill(canvasobject *self, PyObject *args)
{
    int x, y;
    int r = 0, g = 0, b = 0, a = 0;
    PyObject* color;

    if(!PyArg_ParseTuple(args, "iiO", &x, &y, &color))
    {
        PyErr_SetString(PyExc_TypeError, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected two ints and one tuple.");
        return NULL;
    }

    if(PyTuple_Check(color))
    {
        if(PyTuple_GET_SIZE(color) == 4)
        {
            PyObject *rObject = PyTuple_GetItem(color, 0);
            PyObject *gObject = PyTuple_GetItem(color, 1);
            PyObject *bObject = PyTuple_GetItem(color, 2);
            PyObject *aObject = PyTuple_GetItem(color, 3);

            if(PyLong_Check(rObject))
            {
                r = PyLong_AsLong(rObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(rObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(gObject))
            {
                g = PyLong_AsLong(gObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(gObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(bObject))
            {
                b = PyLong_AsLong(bObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(bObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }

            if(PyLong_Check(aObject))
            {
                a = PyLong_AsLong(aObject);
            }
            else
            {
                PyTypeObject *type = (PyTypeObject*)PyObject_Type(aObject);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected type \"int\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            }
        }
        else
        {
            char errorMessageBuffer[1024];

            sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Provided \"color\" has length %i, but expected 4.", PySequence_Fast_GET_SIZE(color));

            PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
            return NULL;
        }
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(color);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Expected \"tuple\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    r = clamp(r, 0, 255);
    g = clamp(g, 0, 255);
    b = clamp(b, 0, 255);
    a = clamp(a, 0, 255);

    unsigned int startColor[4] = {0, 0, 0, 0};

    getPixel(self->data, x, y, self->width, &startColor[0], &startColor[1], &startColor[2], &startColor[3]);

    // Check that we don't try to fill area with the same color as area
    // Without that check we could go in infinite loop
    if(startColor[0] == r && startColor[1] == g && startColor[2] == b && startColor[3] == a)
    {
        Py_INCREF(Py_None);
        return Py_None;
    }

    std::vector<vec2_t> pixels;

    pixels.push_back({x, y});

    setPixel(self->data, x, y, self->width, r, g, b, a);

    while(pixels.size() > 0)
    {
        vec2_t pixel = pixels.back();
        pixels.pop_back();

        if(pixel.x - 1 >= 0)
        {
            if(comparePixelColor(self->data, pixel.x - 1, pixel.y, self->width, startColor[0], startColor[1], startColor[2], startColor[3]))
            {
                pixels.push_back({pixel.x - 1, pixel.y});
                setPixel(self->data, pixel.x - 1, pixel.y, self->width, r, g, b, a);
            }
        }

        if(pixel.x + 1 < self->width)
        {
            if(comparePixelColor(self->data, pixel.x + 1, pixel.y, self->width, startColor[0], startColor[1], startColor[2], startColor[3]))
            {
                pixels.push_back({pixel.x + 1, pixel.y});
                setPixel(self->data, pixel.x + 1, pixel.y, self->width, r, g, b, a);
            }
        }

        if(pixel.y - 1 >= 0)
        {
            if(comparePixelColor(self->data, pixel.x, pixel.y - 1, self->width, startColor[0], startColor[1], startColor[2], startColor[3]))
            {
                pixels.push_back({pixel.x, pixel.y - 1});
                setPixel(self->data, pixel.x, pixel.y - 1, self->width, r, g, b, a);
            }
        }

        if(pixel.y + 1 < self->height)
        {
            if(comparePixelColor(self->data, pixel.x, pixel.y + 1, self->width, startColor[0], startColor[1], startColor[2], startColor[3]))
            {
                pixels.push_back({pixel.x, pixel.y + 1});
                setPixel(self->data, pixel.x, pixel.y + 1, self->width, r, g, b, a);
            }
        }
    }

    pixels.clear();

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *canvas_clear(canvasobject *self, PyObject *args)
{
    for(unsigned int i = 0; i < self->width * self->height * 4; i++)
    {
        self->data[i] = 0;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *canvas_clone(canvasobject *self, PyObject *args)
{
    // Create new Canvas instance
    PyObject *argsList = Py_BuildValue("ii", self->width, self->height);
    PyObject *canvasObject = PyObject_CallObject((PyObject*)&canvas_type, argsList);

    Py_DECREF(argsList);

    // Copy content
    canvasobject *canvas = (canvasobject*)canvasObject;

    for(unsigned int i = 0; i < self->width * self->height * 4; i++)
    {
        canvas->data[i] = self->data[i];
    }

    return canvasObject;
}

}
