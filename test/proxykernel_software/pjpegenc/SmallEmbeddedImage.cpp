// 03/07/2015
// This encoder implemented by David Castells-Rufas (david.castells@uab.cat)
// to do research in parallel implementation of the JPEG encoding algorithm
// The code is implemented in C++ and derived from a Java version, see previous
// author licences below
//
/* GIMP RGB C-Source image dump (test.c) */
#include "SmallEmbeddedImage.h"






int EmbeddedImage::getRGB(int x, int y)
    {
        // const char* pixel = &GIMP_IMAGE_pixel_data[(y*GIMP_IMAGE_WIDTH+x)*GIMP_IMAGE_BYTES_PER_PIXEL];

        char R = x*255/GIMP_IMAGE_WIDTH; // ((pixel[0] - 33) << 2) | ((pixel[1] - 33) >> 4);
        char G = 255; // (((pixel[1] - 33) & 0xF) << 4) | ((pixel[2] - 33) >> 2);
        char B = y*255/GIMP_IMAGE_HEIGHT; // (((pixel[2] - 33) & 0x3) << 6) | (pixel[3] - 33);
        int ARGB = R << 16 | G << 8 | B;

        return ARGB;
    }

void EmbeddedImage::getRGB(int x, int y, int* r, int* g, int* b)
     {
// 	const char* pixel = &GIMP_IMAGE_pixel_data[(y*GIMP_IMAGE_WIDTH+x)*GIMP_IMAGE_BYTES_PER_PIXEL];

        char R = x*255/GIMP_IMAGE_WIDTH; // ((pixel[0] - 33) << 2) | ((pixel[1] - 33) >> 4);
        char G = 255; // (((pixel[1] - 33) & 0xF) << 4) | ((pixel[2] - 33) >> 2);
        char B = y*255/GIMP_IMAGE_HEIGHT; // (((pixel[2] - 33) & 0x3) << 6) | (pixel[3] - 33);

        *r = R;
        *g = G;
        *b = B;
     }

