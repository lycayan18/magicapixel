#include "magicamethods.h"
#include "canvas.h"
#include "pixelutils.h"
#include "clamp.h"

extern "C"
{

PyObject* renderCanvases(PyObject *self, PyObject *args)
{
    int width = 0, height = 0;
    int highlight_x = -1, highlight_y = -1;
    PyObject *canvasesList;

    if(!PyArg_ParseTuple(args, "iiO|ii", &width, &height, &canvasesList, &highlight_x, &highlight_y))
    {
        PyErr_SetString(PyExc_TypeError, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], highlight_x: int = -1, highlight_y: int = -1): Expected two ints, one list and two ints.");
        return NULL;
    }

    if(PySequence_Check(canvasesList))
    {
        unsigned int count = PySequence_Fast_GET_SIZE(canvasesList);
        canvasobject **canvases = new canvasobject*[count];

        if(count == 0)
        {
            Py_INCREF(Py_None);
            return Py_None;
        }

        for(unsigned int i = 0; i < count; i++)
        {
            PyObject* canvas = PySequence_GetItem(canvasesList, i);

            if(!PyCanvas_Check(canvas))
            {
                delete[] canvases;

                PyTypeObject *type = (PyTypeObject*)PyObject_Type(canvas);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas]): Expected \"Canvas\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
                return NULL;
            }

            canvases[i] = (canvasobject*)canvas;
        }

        unsigned char *out = new unsigned char[width * height * 4];

        for(unsigned int y = 0; y < height; y++)
        {
            for(unsigned int x = 0; x < width; x++)
            {
                float r = 0;
                float g = 0;
                float b = 0;
                float a = 0;

                for(unsigned int i = 0; i < count; i++)
                {
                    canvasobject* canvas = canvases[i];

                    unsigned int pixel[4] = {0, 0, 0, 0};

                    getPixel(canvas->data, x, y, width, &pixel[0], &pixel[1], &pixel[2], &pixel[3]);

                    float pixelColorf[4] = {
                        float(pixel[0]) / 255.0f,
                        float(pixel[1]) / 255.0f,
                        float(pixel[2]) / 255.0f,
                        float(pixel[3]) / 255.0f
                    };

                    float a_coef = pixelColorf[3] * (1.0f - a);

                    r = r * a + pixelColorf[0] * a_coef;
                    g = g * a + pixelColorf[1] * a_coef;
                    b = b * a + pixelColorf[2] * a_coef;
                    a = a + a_coef;
                }

                unsigned char outColor[4] = {
                    (unsigned char)(r * 255.0f),
                    (unsigned char)(g * 255.0f),
                    (unsigned char)(b * 255.0f),
                    (unsigned char)(a * 255.0f)
                };

                if(x == highlight_x && y == highlight_y)
                {
                    if(outColor[0] + outColor[1] + outColor[2] < 110 * 3)
                    {
                        outColor[0] = min(outColor[0] + 60, 255);
                        outColor[1] = min(outColor[1] + 60, 255);
                        outColor[2] = min(outColor[2] + 60, 255);
                    }
                    else
                    {
                        outColor[0] = max(outColor[0] - 60, 0);
                        outColor[1] = max(outColor[1] - 60, 0);
                        outColor[2] = max(outColor[2] - 60, 0);
                    }

                    outColor[3] = min(outColor[3] + 200, 255);
                }

                setPixel(out, x, y, width, outColor[0], outColor[1], outColor[2], outColor[3]);
            }
        }

        PyObject *buffer = PyBytes_FromStringAndSize((char*)out, width * height * 4);

        return buffer;
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(canvasesList);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "magicautils.render_canvases(canvases: sequence[Canvas]): Expected \"sequence\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

}
