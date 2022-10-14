#include "clamp.h"

int clamp(int x, int min, int max)
{
    if (x < min)
        return min;

    if (x > max)
        return max;

    return x;
}

int min(int a, int b)
{
    if(a > b)
        return b;

    return a;
}

int max(int a, int b)
{
    if(a > b)
        return a;

    return b;
}
