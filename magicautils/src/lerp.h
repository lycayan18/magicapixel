#ifndef LERP_H
#define LERP_H
#include "color.h"

// Linear interpolate function
float lerp(float a, float b, float x);

// Two dimensional linear interpolate function
float lerp2d(float a, float b, float c, float d, float x, float y);

// Two dimensional linear interpolate function for colors
color4_t lerpRGB2d(color4_t a, color4_t b, color4_t c, color4_t d, float x, float y);

#endif // LERP_H
