#include <cmath>
#include "pixelutils.h"
#include "lerp.h"
#include "color.h"

/*
Helper function.
This function is used in canvas scaling to get correct medium color with alpha taking in account.
Usually scaled image with help of this function looks better than without that function.
*/
void blendColorWithWhite(color4_t *color)
{
    color->r = lerp(255.0f, float(color->r), float(color->a) / 255.0f);
    color->g = lerp(255.0f, float(color->g), float(color->a) / 255.0f);
    color->b = lerp(255.0f, float(color->b), float(color->a) / 255.0f);
}

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

void getPixelSmoothColor(unsigned char *data, float x, float y, int width, int height, unsigned int *r, unsigned int *g, unsigned int *b, unsigned int *a)
{
    color4_t s, t, u, v;

    getPixel(data, x, y, width, &s.r, &s.g, &s.b, &s.a);

    if(x + 1 < width)
    {
        getPixel(data, x + 1, y, width, &t.r, &t.g, &t.b, &t.a);
    }
    else
    {
        t = s;
    }

    if(y + 1 < height)
    {
        getPixel(data, x, y + 1, width, &u.r, &u.g, &u.b, &u.a);
    }
    else
    {
        u = s;
    }

    if(x + 1 < width && y + 1 < height)
    {
        getPixel(data, x + 1, y + 1, width, &v.r, &v.g, &v.b, &v.a);
    }
    else
    {
        if(x + 1 < width)
        {
            v = t;
        }
        else if(y + 1 < height)
        {
            v = u;
        }
        else
        {
            v = s;
        }
    }

    blendColorWithWhite(&s);
    blendColorWithWhite(&t);
    blendColorWithWhite(&u);
    blendColorWithWhite(&v);

    color4_t out = lerpRGB2d(s, t, u, v, x - truncf(x), y - truncf(y));
    *r = out.r;
    *g = out.g;
    *b = out.b;
    *a = out.a;
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
