#define PY_SSIZE_T_CLEAN
#define PY_NO_LINK_LIB
#include "magicautils.h"

extern "C"
{
    /*
    ***************************************************
    **  Export functions
    ***************************************************
    */

    static struct PyMethodDef magicautils_methods[] = {
        {"render_canvases", (PyCFunction)renderCanvases,        METH_VARARGS,   PyDoc_STR("magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas]): Render canvases into bytes raw data.")},
        {NULL, NULL, 0, NULL}
    };

    static struct PyModuleDef magicautilsmodule = {
        .m_base = PyModuleDef_HEAD_INIT,
        .m_name = "magicautils",
        .m_doc = "Magica Pixel's utils library",
        .m_size = -1,
        .m_methods = magicautils_methods
    };


    /*
    ***************************************************
    **  Canvas class
    ***************************************************
    */


    static PyMethodDef canvas_methods[] = {
        {"set_pixel",       (PyCFunction)canvas_setPixel,       METH_VARARGS,   PyDoc_STR("Canvas.set_pixel(x: int, y: int, color: tuple[int, int, int, int]): Sets pixel color.")},
        {"get_pixel",       (PyCFunction)canvas_getPixel,       METH_VARARGS,   PyDoc_STR("Canvas.get_pixel(x: int, y: int): Gets pixel color.")},
        {"resize",          (PyCFunction)canvas_resize,         METH_VARARGS,   PyDoc_STR("Canvas.resize(width: int, height: int): Resizes canvas and clears it.")},
        {"copy_content",    (PyCFunction)canvas_copyContent,    METH_VARARGS,   PyDoc_STR("Canvas.copy_content(target: Canvas): Copies canvas data to target.")},
        {"draw_line",       (PyCFunction)canvas_drawLine,       METH_VARARGS,   PyDoc_STR("Canvas.draw_line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]): Draws line from (x0, y0) to (x1, y1) with provided color ( color replaces with provided, without any alpha blending ).")},
        {"fill",            (PyCFunction)canvas_fill,           METH_VARARGS,   PyDoc_STR("Canvas.fill(x: int, y: int, color: tuple[int, int, int, int]): Flood fills starting from point (x, y) with provided color.")},
        {"clear",           (PyCFunction)canvas_clear,          METH_NOARGS,    PyDoc_STR("Canvas.clear(): Clears canvas image data with color (0, 0, 0, 0).")},
        {NULL, NULL, 0, NULL}
    };

    static struct PyMemberDef canvas_members[] = {
        {NULL}
    };

    extern PyTypeObject canvas_type = {
        .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
        .tp_name = "magicautils.Canvas",
        .tp_basicsize = sizeof(canvasobject),
        .tp_itemsize = 0,
        .tp_dealloc = (destructor)canvas_dealloc,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .tp_methods = canvas_methods,
        .tp_members = canvas_members,
        .tp_init = (initproc)canvas_init,
        .tp_new = canvas_new,
    };

    PyMODINIT_FUNC
    PyInit_magicautils(void)
    {
        PyObject *m;

        if(PyType_Ready(&canvas_type) < 0)
            return NULL;

        m = PyModule_Create(&magicautilsmodule);

        if (m == NULL)
            return NULL;

        Py_INCREF(&canvas_type);

        if(PyModule_AddObject(m, "Canvas", (PyObject*)&canvas_type) < 0)
        {
            Py_DECREF(&canvas_type);
            Py_DECREF(m);

            return NULL;
        }

        return m;
    }
}
