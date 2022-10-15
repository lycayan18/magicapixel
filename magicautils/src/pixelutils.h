#ifndef PIXELUTILS_H
#define PIXELUTILS_H
/*
Utils for working with pixels: get index of pixel, set pixel color in data, compare pixels.
*/

void setPixel(unsigned char *data, int x, int y, int width, unsigned int r, unsigned int g, unsigned int b, unsigned int a);
void getPixel(unsigned char *data, int x, int y, int width, unsigned int *r, unsigned int *g, unsigned int *b, unsigned int *a);

/*
Gets pixel color in fractional coordinates (x, y).
Returns linearly interpolated ( smooth ) color of near to (x, y) 4 pixels.
*/
void getPixelSmoothColor(unsigned char *data, float x, float y, int width, int height, unsigned int *r, unsigned int *g, unsigned int *b, unsigned int *a);
bool comparePixelColor(unsigned char *data, int x, int y, int width, unsigned int r, unsigned int g, unsigned int b, unsigned int a);

#endif // PIXELUTILS_H
