#include "pixelutils.h"

void setPixel(unsigned char *data, int x, int y, int width, unsigned int r, unsigned int g, unsigned int b, unsigned int a)
{
    unsigned int pixelIndex = x + y * width;
    data[pixelIndex * 4] = r;
    data[pixelIndex * 4 + 1] = g;
    data[pixelIndex * 4 + 2] = b;
    data[pixelIndex * 4 + 3] = a;
}

void getPixel(unsigned char *data, int x, int y, int width, unsigned int *r, unsigned int *g, unsigned int *b, unsigned int *a)
{
    unsigned int pixelIndex = x + y * width;
    *r = data[pixelIndex * 4];
    *g = data[pixelIndex * 4 + 1];
    *b = data[pixelIndex * 4 + 2];
    *a = data[pixelIndex * 4 + 3];
}

bool comparePixelColor(unsigned char *data, int x, int y, int width, unsigned int r, unsigned int g, unsigned int b, unsigned int a)
{
    unsigned int pixelIndex = x + y * width;

    if(data[pixelIndex * 4] != r)
        return false;

    if(data[pixelIndex * 4 + 1] != g)
        return false;

    if(data[pixelIndex * 4 + 2] != b)
        return false;

    if(data[pixelIndex * 4 + 3] != a)
        return false;

    return true;
}
