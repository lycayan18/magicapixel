#ifndef CANVAS_H
#define CANVAS_H

#include <Python.h>
#include <structmember.h>
#define PyCanvas_Check(o) PyObject_TypeCheck(o, &canvas_type)

extern "C"
{
    extern PyTypeObject canvas_type;

    typedef struct
    {
        PyObject_HEAD
        unsigned char *data;
        unsigned int width;
        unsigned int height;
    } canvasobject;

    extern PyObject *canvas_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
    extern void canvas_dealloc(canvasobject *self);
    extern int canvas_init(canvasobject *self, PyObject *arts, PyObject *kwds);

    extern PyObject *canvas_setPixel(canvasobject *self, PyObject *args);
    extern PyObject *canvas_getPixel(canvasobject *self, PyObject *args);
    extern PyObject *canvas_resize(canvasobject *self, PyObject *args);
    extern PyObject *canvas_copyContent(canvasobject *self, PyObject *args);
    extern PyObject *canvas_drawLine(canvasobject *self, PyObject *args);
    extern PyObject *canvas_fill(canvasobject *self, PyObject *args);
    extern PyObject *canvas_clear(canvasobject *self, PyObject *args);
    extern PyObject *canvas_clone(canvasobject *self, PyObject *args);
}

#endif // CANVAS_H
