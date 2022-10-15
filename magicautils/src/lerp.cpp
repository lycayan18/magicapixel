#include "lerp.h"

// Linear interpolate function
float lerp(float a, float b, float x)
{
    return a + (b - a) * x;
}

// Two dimensional linear interpolate function
float lerp2d(float a, float b, float c, float d, float x, float y)
{
    float s = a + (b - a) * x;
    float t = c + (d - c) * x;

    return s + (t - s) * y;
}

color4_t lerpRGB2d(color4_t a, color4_t b, color4_t c, color4_t d, float x, float y)
{
    return {
        (unsigned int)lerp2d(a.r, b.r, c.r, d.r, x, y),
        (unsigned int)lerp2d(a.g, b.g, c.g, d.g, x, y),
        (unsigned int)lerp2d(a.b, b.b, c.b, d.b, x, y),
        (unsigned int)lerp2d(a.a, b.a, c.a, d.a, x, y)
    };
}
