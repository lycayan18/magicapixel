#include <iostream>
#include "magicamethods.h"
#include "canvas.h"
#include "pixelutils.h"
#include "clamp.h"
#include "alphablending.h"

extern "C"
{

PyObject* renderCanvases(PyObject *self, PyObject *args)
{
    int width = 0, height = 0;
    int highlight_x = -1, highlight_y = -1;
    PyObject *canvasesList;
    PyObject *alphaBlendingsList;

    if(!PyArg_ParseTuple(args, "iiOO|ii", &width, &height, &canvasesList, &alphaBlendingsList, &highlight_x, &highlight_y))
    {
        PyErr_SetString(PyExc_TypeError, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): Expected two ints, one list and two ints.");
        return NULL;
    }

    // Check that alphaBlendingsList is a sequence
    if(!PySequence_Check(alphaBlendingsList))
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(alphaBlendingsList);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): Expected \"sequence\" in \"alpha_blendings\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    if(PySequence_Check(canvasesList))
    {
        long count = PySequence_Fast_GET_SIZE(canvasesList);

        // Check that alphaBlendingsList and canvasesList have identical size
        if(PySequence_Fast_GET_SIZE(alphaBlendingsList) != count)
        {
            PyErr_SetString(PyExc_ValueError, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): \"canvases\" and \"alpha_blendings\" have different sizes.");
            return NULL;
        }

        if(count == 0)
        {
            Py_INCREF(Py_None);
            return Py_None;
        }

        canvasobject **canvases = new canvasobject*[count];
        int *alphaBlendingModes = new int[count];

        for(unsigned int i = 0; i < count; i++)
        {
            PyObject* canvas = PySequence_Fast_GET_ITEM(canvasesList, i);
            PyObject* alphaBlendingMode = PySequence_Fast_GET_ITEM(alphaBlendingsList, i);

            if(!PyLong_Check(alphaBlendingMode))
            {
                delete[] canvases;
                delete[] alphaBlendingModes;

                PyTypeObject *type = (PyTypeObject*)PyObject_Type(alphaBlendingMode);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): Expected \"int\" in \"alpha_blendings\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
                return NULL;
            }

            if(!PyCanvas_Check(canvas))
            {
                delete[] canvases;
                delete[] alphaBlendingModes;

                PyTypeObject *type = (PyTypeObject*)PyObject_Type(canvas);
                char errorMessageBuffer[1024];

                sprintf(errorMessageBuffer, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): Expected \"Canvas\" in \"canvases\", but got \"%s\".", type->tp_name);

                PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
                return NULL;
            }

            canvases[i] = (canvasobject*)canvas;
            alphaBlendingModes[i] = PyLong_AsLong(alphaBlendingMode);
        }

        unsigned char *out = new unsigned char[width * height * 4];

        // TODO: Think about rendering optimizations ( delta-rendering )

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
                    int alphaBlendingMode = alphaBlendingModes[i];

                    unsigned int pixel[4] = {0, 0, 0, 0};

                    getPixel(canvas->data, x, y, width, &pixel[0], &pixel[1], &pixel[2], &pixel[3]);

                    float pixelColorf[4] = {
                        float(pixel[0]) / 255.0f,
                        float(pixel[1]) / 255.0f,
                        float(pixel[2]) / 255.0f,
                        float(pixel[3]) / 255.0f
                    };

                    switch(alphaBlendingMode)
                    {
                    case AlphaBlendingMode::ADD:
                    {
                        r += pixelColorf[0] * pixelColorf[3];
                        g += pixelColorf[1] * pixelColorf[3];
                        b += pixelColorf[2] * pixelColorf[3];
                        a += pixelColorf[3];
                        break;
                    }
                    case AlphaBlendingMode::OVER:
                    {
                        float a_coef = a * (1.0f - pixelColorf[3]);
                        float out_a = pixelColorf[3] + a_coef;

                        if(out_a == 0.0f)
                        {
                            break;
                        }

                        r = (pixelColorf[0] * pixelColorf[3] + r * a_coef) / out_a;
                        g = (pixelColorf[1] * pixelColorf[3] + g * a_coef) / out_a;
                        b = (pixelColorf[2] * pixelColorf[3] + b * a_coef) / out_a;
                        a = out_a;
                        break;
                    }
                    }
                }

                r = clampf(r, 0.0f, 1.0f);
                g = clampf(g, 0.0f, 1.0f);
                b = clampf(b, 0.0f, 1.0f);
                a = clampf(a, 0.0f, 1.0f);

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

        delete[] out;
        delete[] canvases;
        delete[] alphaBlendingModes;

        return buffer;
    }
    else
    {
        PyTypeObject *type = (PyTypeObject*)PyObject_Type(canvasesList);
        char errorMessageBuffer[1024];

        sprintf(errorMessageBuffer, "magicautils.render_canvases(width: int, height: int, canvases: sequence[Canvas], alpha_blendings: sequence[int], highlight_x: int = -1, highlight_y: int = -1): Expected \"sequence\" in \"canvases\", but got \"%s\".", type->tp_name);

        PyErr_SetString(PyExc_TypeError, errorMessageBuffer);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

}
